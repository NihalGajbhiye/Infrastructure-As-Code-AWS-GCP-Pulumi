import pulumi
from pulumi_aws import ec2
import pulumi_aws as aws


config = pulumi.Config()

#Configuration loading
stack_name = pulumi.get_stack()
vpc_name = config.require("vpcName")
vpc_cidr_block = config.require("vpcCIDRBlock")
subnet_count = int(config.get("subnetCount") or 2)
cidr_base = config.require("cidrBase")


vpc_name_full = f"{stack_name}-{vpc_name}"
cidr_base_start, cidr_base_subnet = (
    cidr_base.split("/")[0].rsplit(".",2)[0],
    cidr_base.split("/")[1]
)

# Creating VPC
vpc = ec2.Vpc(
    vpc_name_full,
    cidr_block=vpc_cidr_block,
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": vpc_name_full}
)

# Determine available AZs
available_azs = aws.get_availability_zones(state="available")
az_count = min(len(available_azs.names), subnet_count)

# Create subnets across the AZs
public_subnets =[]
private_subnets = []

for i in range(az_count):
    try:
        public_sub_name = f"{vpc_name_full}-pub-subnet-{i}"
        private_sub_name = f"{vpc_name_full}-pri-subnet-{i}"

        pub_subnet = ec2.Subnet(
            public_sub_name,
            vpc_id = vpc.id,
            cidr_block = f"{cidr_base_start}.{2*i}.0/{cidr_base_subnet}",
            map_public_ip_on_launch = True,
            availability_zone = available_azs.names[i],
            tags = {"Name": public_sub_name}
        )

        pri_subnet = ec2.Subnet(
            private_sub_name,
            vpc_id = vpc.id,
            cidr_block = f"{cidr_base_start}.{2*i+1}.0/{cidr_base_subnet}",
            map_public_ip_on_launch = True,
            availability_zone = available_azs.names[i],
            tags = {"Name": private_sub_name}
        )

        public_subnets.append(pub_subnet)
        private_subnets.append(pri_subnet)

    except Exception as e:
        raise pulumi.RunError(f"Failed to create subnets: {str(e)}")
    
# Create Internet Gateway
igw = ec2.InternetGateway(
    f"{vpc_name_full}-igw",
    vpc_id=vpc.id,
    opts = pulumi.ResourceOptions(depends_on=[vpc]),
    tags = {"Name": f"{vpc_name}_igw"}
)

# Create Route Table
public_route_table = ec2.RouteTable(
    f"{vpc_name_full}-public-route-table",
    vpc_id=vpc.id,
    opts = pulumi.ResourceOptions(depends_on=[vpc]),
    tags = {"Name": f"{vpc_name}_public_route_table"}
)

# Associate our subnet with Route table
for i, subnet in enumerate(public_subnets):
    route_table_assoc = ec2.RouteTableAssociation(
        f"{vpc_name_full}-pub-rta-{i}",
        subnet_id =subnet.id,
        route_table_id=public_route_table.id,
        opts= pulumi.ResourceOptions(depends_on=[public_route_table, subnet])
    )

# Add a route to Route Table that points to Internet Gateway
route_to_internet =ec2.Route(
    f"{vpc_name_full}-route-to-internet",
    route_table_id= public_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=igw.id,
    opts=pulumi.ResourceOptions(depends_on=[public_route_table, igw])
)

# Create a private Route Table
private_route_table = ec2.RouteTable(
    f"{vpc_name_full}-private-route-table",
    vpc_id=vpc.id,
    opts= pulumi.ResourceOptions(depends_on=[vpc]),
    tags={"Name": f"{vpc_name}-private-route-table"}
)

# Associate private subnet with Route Table 
for i, subnet in enumerate(private_subnets):
    route_table_assoc = ec2.RouteTableAssociation(
        f"{vpc_name_full}-private-rta-{i}",
        subnet_id=subnet.id,
        route_table_id=private_route_table.id,
        opts=pulumi.ResourceOptions(depends_on=[private_route_table, subnet])
    )

# Export necessart details
pulumi.export("vpcId", vpc.id)
pulumi.export("subnetsId", [subnet.id for subnet in public_subnets])
pulumi.export("privateSubnetsIds", [subnet.id for subnet in private_subnets])


