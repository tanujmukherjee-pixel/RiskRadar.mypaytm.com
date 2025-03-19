1. Receive Alert Notification
Monitor for alerts related to disk utilization exceeding 75% on any node within the EKS cluster.

2. Extract Alert Details
- Extract the cluster name and node name from the alert context.
- Ensure the node name is in the correct internal DNS hostname format. Convert if necessary.

3. Self-Heal Action
- Install AWS CLI: Ensure AWS CLI and Session Manager Plugin are installed on the node.
- Get Instance ID: Retrieve the instance ID for the node using the node name.
- Clean Up Node: Execute cleanup operations on the node to free up disk space.

4. Check Node Labels and Take Action
- Cordon or Drain: Based on node labels, decide whether to cordon or drain the node.
-- Cordon: If the label key is eks.amazonaws.com/capacityType=ON_DEMAND.
-- Drain: If the label key is karpenter.sh/capacity-type=on-demand.

5. Node Cordoning
- If the node is not already cordoned, mark it as unschedulable.

6. Node Draining
If draining is required, evict all non-DaemonSet pods from the node.
Ensure no critical pods (e.g., Rule Engine pods) are running before draining.