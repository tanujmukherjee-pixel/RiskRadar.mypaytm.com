import subprocess
import logging
import shutil
import os
import boto3
import time
from kubernetes import client, config

def get_dns_hostname(instance_name: str) -> str:
    # Convert node name to internal DNS hostname format if necessary
    if not (instance_name.startswith("ip-") and instance_name.endswith(".compute.internal")):
        if ":" in instance_name:
            instance_ip = instance_name.split(":")[0]  # Extract the IP address part
        else:
            instance_ip = instance_name

        if instance_ip.count(".") == 3:  # Ensure it's a valid IPv4 address
            ip_parts = instance_ip.split(".")
            instance_name = f"ip-{ip_parts[0]}-{ip_parts[1]}-{ip_parts[2]}-{ip_parts[3]}.ap-south-1.compute.internal"
            return f"Converted to internal DNS hostname: {instance_name}"
        else:
            return f"Invalid instance name format: {instance_name}"
    return instance_name

def install_awscli():
    print("Installing AWS CLI")

    try:
        # Check if AWS CLI is already installed without using check=True
        aws_exists = shutil.which('aws') is not None
        if aws_exists:
            aws_version = subprocess.run("aws --version", shell=True, capture_output=True, text=True)
            logging.info("AWS CLI is already installed")
            logging.info(f"AWS CLI version: {aws_version.stdout.strip()}")
        else:
            # Install AWS CLI
            logging.info("Installing AWS CLI...")
            # Change to /tmp directory and perform installation
            os.chdir('/tmp')
            
            # Download AWS CLI
            subprocess.run(
                "curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'",
                shell=True, check=True
            )
            
            # Install unzip
            subprocess.run(
                "apt-get update && apt-get install unzip -y",
                shell=True, check=True
            )
            
            # Unzip and install AWS CLI
            subprocess.run("unzip -q awscliv2.zip", shell=True, check=True)
            subprocess.run("./aws/install", shell=True, check=True)
            
            # Clean up
            subprocess.run("rm -rf awscliv2.zip aws", shell=True, check=True)
            logging.info("Successfully installed AWS CLI")

        # Check if Session Manager Plugin is already installed without using check=True
        ssm_exists = shutil.which('session-manager-plugin') is not None
        if ssm_exists:
            ssm_version = subprocess.run("session-manager-plugin --version", shell=True, capture_output=True, text=True)
            logging.info("Session Manager Plugin is already installed")
            logging.info(f"Session Manager Plugin version: {ssm_version.stdout.strip()}")
        else:
            # Install Session Manager Plugin
            logging.info("Installing Session Manager Plugin...")
            # Change to /tmp directory and perform installation
            os.chdir('/tmp')
            
            # Download and install Session Manager Plugin
            subprocess.run(
                "curl 'https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm' -o 'session-manager-plugin.rpm'",
                shell=True, check=True
            )
            subprocess.run("sudo rpm -i session-manager-plugin.rpm", shell=True, check=True)
            
            # Clean up
            subprocess.run("rm -f session-manager-plugin.rpm", shell=True, check=True)
            logging.info("Successfully installed Session Manager Plugin")

        # Final verification
        aws_final = subprocess.run("aws --version", shell=True, capture_output=True, text=True)
        ssm_final = subprocess.run("session-manager-plugin --version", shell=True, capture_output=True, text=True)
        
        logging.info(f"Final AWS CLI version: {aws_final.stdout.strip()}")
        logging.info(f"Final Session Manager Plugin version: {ssm_final.stdout.strip()}")

        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Error during AWS CLI or Session Manager Plugin installation: {str(e)}")
        logging.error(f"Command output: {e.stdout if hasattr(e, 'stdout') else 'No stdout available'}")
        logging.error(f"Command error: {e.stderr if hasattr(e, 'stderr') else 'No stderr available'}")
        logging.error(f"Return code: {e.returncode}")
        raise

    except Exception as e:
        logging.error(f"Unexpected error during AWS CLI or Session Manager Plugin installation: {str(e)}")
        raise

def get_node_instance_id(private_dns_name):
    """
    Get the instance ID of a node using the Private IP DNS name.

    :param private_dns_name: The private DNS name of the EC2 instance.
    :return: The instance ID if found, otherwise error.
    """

    # Initialize EC2 client
    ec2_client = boto3.client('ec2', region_name='ap-south-1')

    try:
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'private-dns-name', 'Values': [private_dns_name]}
            ]
        )

        # Check if any reservations exist
        if not response['Reservations']:
            raise Exception(f"No instances found with private DNS name: {private_dns_name}")

        # Check if any instances exist in the first reservation
        if not response['Reservations'][0]['Instances']:
            raise Exception(f"No instances found in reservation for DNS name: {private_dns_name}")

        instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
        return instance_id

    except Exception as e:
        logging.error(f"Error getting instance ID for node {private_dns_name}: {str(e)}")
        raise

def clean_up_node(instance_id):
    logging.info(f"Starting cleanup for instance ID: {instance_id}")

    # Create the AWS command to send the shell script
    send_command = f'''aws ssm send-command \
        --instance-ids "{instance_id}" \
        --document-name "AWS-RunShellScript" \
        --parameters '{{"commands":[
            "echo \\"Clean Up Yum Cache (Package Manager Cache)\\"",
            "sudo yum clean all",
            "sudo rm -rf /var/cache/yum/*",
            "echo \\"Truncating Log Files, instead of deleting\\"",
            "sudo find /var/log/ -type f -name \\"*.log\\" -exec truncate -s 0 {{}} \\\;",
            "echo \\"Cleaning up journalctl\\"",
            "sudo journalctl --vacuum-time=1d",
            "echo \\"Cleaning up old containerd metadata\\"",
            "sudo rm -rf /var/lib/containerd/tmp/*",
            "echo \\"List information about block devices\\"",
            "lsblk"
        ]}}' \
        --region ap-south-1 \
        --output text \
        --query "Command.CommandId"'''

    try:
        # Execute send-command and get the command ID
        logging.debug(f"Executing command: {send_command}")
        result = subprocess.run(send_command, shell=True, check=True, capture_output=True, text=True)
        command_id = result.stdout.strip()
        
        if not command_id:
            raise Exception("Failed to get command ID from send-command")
        
        logging.info(f"Successfully sent cleanup command. Command ID: {command_id}")
        
        # Wait for command to complete and get output
        max_retries = 10
        retry_count = 0
        while retry_count < max_retries:
            get_output_command = f'''aws ssm list-command-invocations \
                --command-id {command_id} \
                --details \
                --region ap-south-1 \
                --query "CommandInvocations[0].CommandPlugins[0].Output" \
                --output text'''
                
            output_result = subprocess.run(get_output_command, shell=True, check=True, capture_output=True, text=True)
            output = output_result.stdout.strip()
            
            if output and output != "None":
                logging.info("Cleanup operation results:")
                logging.info("=" * 50)
                logging.info(output)
                logging.info("=" * 50)
                return output
                
            logging.info(f"Waiting for cleanup command completion. Attempt {retry_count + 1}/{max_retries}")
            time.sleep(5)
            retry_count += 1
            
        raise Exception(f"Command did not complete after {max_retries} retries")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {str(e)}")
        logging.error(f"Command stdout: {e.stdout if hasattr(e, 'stdout') else 'No stdout available'}")
        logging.error(f"Command stderr: {e.stderr if hasattr(e, 'stderr') else 'No stderr available'}")
        logging.error(f"Return code: {e.returncode}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise

def get_node(node_name: str):
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()

    try:
        node = v1.read_node(name=node_name)
    except client.exceptions.ApiException as e:
        error_message = f"Failed to read node {node_name}: {e}"
        print(error_message)

    return node

def drain_node(node_name: str):
    node = get_node(node_name)
    v1 = client.CoreV1Api()

    try:
        pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node.metadata.name}").items
        if not pods:
            return f"Node {node.metadata.name} is already drained (no pods scheduled)."
            
        # Check for rule engine pods
        elif any(pod.metadata.name.startswith("pi-rule-engine-") for pod in pods):
            # Uncordon the node
            try:
                v1.patch_node(node.metadata.name, {"spec": {"unschedulable": False}})
            except Exception as e:
                error_message = f"Failed to uncordon node {node.metadata.name}: {e}"
                logging.error(error_message)
            return f"Node {node.metadata.name} has Rule Engine pods scheduled. Not Draining the node"
        else:
            for pod in pods:
                if pod.metadata.owner_references and any(owner.kind == "DaemonSet" for owner in pod.metadata.owner_references):
                    logging.info(f"Skipping deletion of pod {pod.metadata.name} from DaemonSet on node {node.metadata.name}.")
                else:
                    try:
                        v1.delete_namespaced_pod(name=pod.metadata.name, namespace=pod.metadata.namespace)
                        logging.info(f"Pod {pod.metadata.name} deleted from node {node.metadata.name}.")
                    except Exception as e:
                        error_message = f"Failed to delete pod {pod.metadata.name}: {e}"
                        logging.error(error_message)
            return f"Node {node.metadata.name} drained (all pods evicted)."
    except Exception as e:
        error_message = f"Failed to drain node {node.metadata.name}: {e}"
        logging.error(error_message)
        raise error_message

def cordon_node(node_name: str):
    node = get_node(node_name)
    v1 = client.CoreV1Api()
    try:
        v1.patch_node(node.metadata.name, {"spec": {"unschedulable": True}})
        logging.info(f"Node {node.metadata.name} cordoned successfully.")
    except Exception as e:
        error_message = f"Failed to cordon node {node.metadata.name}: {e}"
        logging.error(error_message)
        raise error_message

def uncordon_node(node_name: str):
    node = get_node(node_name)
    v1 = client.CoreV1Api()
    try:
        v1.patch_node(node.metadata.name, {"spec": {"unschedulable": False}})
        logging.info(f"Node {node.metadata.name} uncordoned successfully.")
    except Exception as e:
        error_message = f"Failed to uncordon node {node.metadata.name}: {e}"
        logging.error(error_message)
        raise error_message


