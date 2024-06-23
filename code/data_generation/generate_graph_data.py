import pandas as pd
from langchain_community.graphs import Neo4jGraph
import os
from dotenv import load_dotenv
load_dotenv()

# Initialise graph
def connect_to_graph():
    try:
        graph = Neo4jGraph(
            url=os.getenv("NEO4j_DB_URL"),
            username="neo4j",
            password=os.getenv("NEO4J_PASSWORD")
        )
        return graph
    except Exception as e:
        print(e)
        print("Error in connecting to graph")
        raise e

def insert_vpc_data(graph, vpc_data):
    query = """
    UNWIND $vpcs AS vpc
    MERGE (v:VPC {vpc_id: vpc.vpc_id})
    ON CREATE SET v.vpc_name = vpc.vpc_name,
                  v.region = vpc.region,
                  v.cidr_block = vpc.cidr_block,
                  v.is_default = vpc.is_default
    """
    graph.query(query, params={"vpcs": vpc_data})

def insert_ec2_data(graph, ec2_data):
    query = """
    UNWIND $ec2s AS ec2
    MERGE (e:EC2 {instance_id: ec2.instance_id})
    ON CREATE SET e.instance_type = ec2.instance_type,
                  e.state = ec2.state,
                  e.launch_time = ec2.launch_time,
                  e.public_ip = ec2.public_ip
    WITH e, ec2
    MATCH (v:VPC {vpc_id: ec2.vpc_id})
    MERGE (e)-[:LAUNCHED_IN]->(v)
    """
    graph.query(query, params={"ec2s": ec2_data})

def load_csv_data(file_path):
    # get current directory
    path = os.path.dirname(__file__) + "/" + file_path
    return pd.read_csv(path).to_dict(orient='records')

def generate_graph_data():
    vpc_data = load_csv_data('vpc.csv')
    ec2_data = load_csv_data('ec2.csv')

    graph = connect_to_graph()

    insert_vpc_data(graph, vpc_data)
    insert_ec2_data(graph, ec2_data)

if __name__ == "__main__":
    generate_graph_data()
