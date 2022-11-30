## Brightside deployment
This application is deployed on a GKE Cluster (Google K8s Engine) with a supporting Cloud SQL PG instance.
The connection between the incident-bot container and CloudSQL is handled via a CloudSQL Proxy "Sidecar" container.

For now, deployment of infrastructure is done through Terraform Cloud and PRs in the mcnulty repo.

[TBD] In the future any updates to the environment and the application can be handled with CI, if we find ourselves touching this codebase frequently enough.

### Deployment (from local CLI)

#### Authenticating with Google Cloud for GKE & CloudSQL Management

```
gcloud auth login
gcloud config set project brightside-prod # or brightside-dev-363022 for dev

# get cluster credentials
gcloud container clusters get-credentials gke-slackbots-1-prod # or gke-slackbots-1 for dev
```

#### Setting Secrets & Environment Variables

Be sure to create the appropriate db user for the incident-bot PG databse in Cloud SQL and create the secrets for the env var in GKE.
cfg-secrets.yml is stored in 1Password for the time being. This file includes all required environment variables for incident-bot.

```
kubectl create secret generic incident-bot --from-env-file cfg-secrets.yml --namespace=slackbots
```

If you need to update or replace secret values, just delete and recreate them and scale down to zero & up, eg:

```
kubectl delete secret incident-bot
kubectl create secret generic incident-bot --from-env-file cfg-secrets.yml --namespace=slackbots
kubectl scale deployment incident-bot --replicas=0 -n slackbots
kubectl scale deployment incident-bot --replicas=1 -n slackbots
```

#### Database Authentication

If the CloudSQL PG instance is newly provisioned, you must update the built in user `postgres` first!. Make sure to add the password to the secrets config file in 1Password and replace the incident-bot secrets in GKE.

You can get the instance name by invoking `gcloud sql instances list`.

```
gcloud sql users set-password postgres \
--instance=INSTANCE_NAME \
--prompt-for-password
```

#### Build & Deploy

Dev: `gcloud builds submit --project=brightside-dev-363022 --config cloudbuild.dev.yml --region=us-central1`

Prod: `gcloud builds submit --project=brightside-prod --config cloudbuild.prod.yml --region=us-central1`

#### CI/CD Flow [To-Do]

- Figure out [Rolling Update](https://cloud.google.com/kubernetes-engine/docs/how-to/updating-apps) for containers in GKE pods (we have two - Cloud SQL Auth Proxy + incident-bot)
- [Hint](https://stackoverflow.com/a/40368520/5842023)

### Restarting the App

Since we have multiple containers in our pod (incident-bot and the CloudSQL Auth Proxy container), we have to use a scale event to essentially "restart" the application. The app is stateless as far as our deployments are concerned, so just scale down and up.

```
# down
kubectl scale deployment incident-bot --replicas=0 -n slackbots
# up
kubectl scale deployment incident-bot --replicas=1 -n slackbots
```

### Scaling incident-bot

This works the same way "restarting" via a scale event does:

```
kubectl scale deployment incident-bot --replicas=<desired capacity> -n slackbots
```

## incident-bot (Vanilla Docs)

<img src="https://github.com/echoboomer/incident-bot/blob/main/assets/bot.png" width="125" height="125">

![tests](https://github.com/echoboomer/incident-bot/actions/workflows/tests.yml/badge.svg)
![version](https://img.shields.io/github/v/release/echoboomer/incident-bot)

Incident management ChatOps bot for Slack to allow your teams to easily and effectively identify and manage technical incidents impacting your cloud infrastructure, your products, or your customers' ability to use your applications and services.

Interacting with the bot is incredibly easy through the use of modals and simplified commands.

[View documentation on readthedocs](https://incident-bot.readthedocs.io/en/latest/)

<img src="https://github.com/echoboomer/incident-bot/blob/main/assets/incident-bot-demo-1.gif" width="700" height="500" />

- [incident-bot](#incident-bot)
  - [Features at a Glance](#features-at-a-glance)
  - [Architecture](#architecture)
  - [Requirements](#requirements)
  - [Documentation](#documentation)
  - [Testing](#testing)
  - [Feedback](#feedback)

## Features at a Glance

- Fully featured web management UI
- Robust experience in Slack to create and manage incidents using actions, shortcuts, and modals
- Automatic creation of a centralized incident channel to partition conversation about incidents
- Automatically page teams (if PagerDuty integration is enabled) on incident creation and/or on-demand
- Select messages to pin to the incident that can be displayed in the web UI and automatically added to the RCA document
- Automatically create an RCA channel and an RCA document (if Confluence integration is enabled)
- Optional integration to manage Statuspage incidents directly from the Slack channel
- Optional integration to automatically fetch the status of upstream providers

## Architecture

The app is written in Python and backed by Postgresql and leverages the `slack-bolt` websocket framework to provide zero footprint for security concerns.

The web UI is written in React.

Each incident stores unique data referenced by processes throughout the app for lifecycle management on creation. The database should be durable and connection information should be passed to the application securely. In the event that a record is lost while an incident is open, the bot will be unable to manage that incident and none of the commands will work.

## Requirements

- [Create a Slack app](https://api.slack.com/apps?new_app=1) for this application. You can name it whatever you'd like, but `incident-bot` seems to make the most sense.
- Use the option to create the app from a manifest. Run `make render` to output `slack_app_manifest.yaml` at project root and paste in the contents. You can adjust these settings later as you see fit, but these are the minimum permissions required for the bot to function properly.
- Install the app to your workspace. You'll now have an OAuth token. Provide that as `SLACK_BOT_TOKEN`.
- Verify that websocket mode is enabled and provide the generated app token as `SLACK_APP_TOKEN` - you can generate an app token via the `Basic Information` page in your app's configuration.

## Documentation

The documentation covers all setup requirements and features of the app.

[View on readthedocs](https://incident-bot.readthedocs.io/en/latest/)

## Testing

Tests will run on each pull request and merge to the primary branch. To run them locally:

```bash
$ make -C backend run-tests
```

## Feedback

This application is not meant to solve every problem with regard to incident management. It was created as an open-source alternative to paid solutions that integrate with Slack.

If you encounter issues with functionality or wish to see new features, please open an issue and let us know.
