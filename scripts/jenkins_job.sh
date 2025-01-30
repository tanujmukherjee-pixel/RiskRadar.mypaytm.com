#!/bin/bash

# Configuration
JENKINS_URL="https://central-jenkins.paytmdgt.io"
JOB_NAME="Gradle-Nexus-Java17"
PARAMS="BB_REPO_NAME=${1:?BB_REPO_NAME must be provided}&BB_SOURCE_BRANCH=${1:?BB_BRANCH must be provided}"
USER="NEXUS_USER_REDACTED"
PASSWORD="${NEXUS_PASSWORD:?NEXUS_PASSWORD env var must be set}"
AUTH_HEADER=$(echo -n "$USER:$PASSWORD" | base64)

# Function to fetch the Jenkins crumb and cookies
get_jenkins_crumb_and_cookies() {
  echo "Fetching Jenkins crumb and cookies..."

  # Fetch the crumb and save cookies to a temporary file
  CRUMB_RESPONSE=$(curl -s -u "$USER:$PASSWORD" --cookie-jar /tmp/jenkins_cookies.txt "$JENKINS_URL/crumbIssuer/api/json")
  CRUMB=$(echo "$CRUMB_RESPONSE" | jq -r '.crumb')
  CRUMB_HEADER=$(echo "$CRUMB_RESPONSE" | jq -r '.crumbRequestField')

  if [ -z "$CRUMB" ] || [ -z "$CRUMB_HEADER" ]; then
    echo "Failed to fetch Jenkins crumb."
    exit 1
  fi

  echo "Crumb fetched successfully"
}

# Fetch Jenkins crumb and cookies
get_jenkins_crumb_and_cookies

# Extract cookies from the cookie file
COOKIES=$(awk '{print $6 "=" $7}' /tmp/jenkins_cookies.txt | tr '\n' ';')

# Trigger the Jenkins job with parameters
echo "Triggering Jenkins job with parameters..."
TRIGGER_RESPONSE=$(curl -s --location --request POST "$JENKINS_URL/job/$JOB_NAME/buildWithParameters?$PARAMS" \
  --header "$CRUMB_HEADER: $CRUMB" \
  --header "Authorization: Basic $AUTH_HEADER" \
  --header "Cookie: $COOKIES")

if [ $? -ne 0 ]; then
  echo "Failed to trigger Jenkins job."
  exit 1
fi

echo "Job triggered successfully."

# Get the queue item to fetch the build number
BUILD_NUMBER=""
QUEUE_URL="$JENKINS_URL/job/$JOB_NAME/lastBuild/api/json"
while [ -z "$BUILD_NUMBER" ]; do
  BUILD_NUMBER=$(curl -s -u "$USER:$PASSWORD" -H "$CRUMB_HEADER: $CRUMB" --header "Cookie: $COOKIES" "$QUEUE_URL" | jq -r '.number')
  sleep 5
done

echo "Jenkins job started with build number: $BUILD_NUMBER"

# Check the status of the job until it's complete
BUILD_STATUS=""
while [ "$BUILD_STATUS" != "SUCCESS" ] && [ "$BUILD_STATUS" != "FAILURE" ] && [ "$BUILD_STATUS" != "ABORTED" ]; do
  BUILD_STATUS=$(curl -s -u "$USER:$PASSWORD" -H "$CRUMB_HEADER: $CRUMB" --header "Cookie: $COOKIES" "$JENKINS_URL/job/$JOB_NAME/$BUILD_NUMBER/api/json" | jq -r '.result')
  echo "Checking status... Current status: ${BUILD_STATUS:-IN PROGRESS}"
  sleep 10
done

# Print the final status
if [ "$BUILD_STATUS" == "SUCCESS" ]; then
  echo "Jenkins job completed successfully."
else
  echo "Jenkins job failed with status: $BUILD_STATUS"
  exit 1
fi

echo "Done"
