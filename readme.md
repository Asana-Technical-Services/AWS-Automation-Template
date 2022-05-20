# AWS AUTOMATION TEMPLATE

This project contains source code foundation and supporting files for a deploying an automation in AWS

## Architecture

This project is an AWS serverless application that you is deployed via a github action using AWS SAM. It includes the following files and folders.

- _apiHandler/_ - The application's main Lambda function which handles incoming API requests, validates them, and triggers a state machine to handle any further actions if necessary.

- _PortfolioUpdatedHandler/_ - A Lambda function triggered when a new project is added to the "Form Automation Projects" portfolio. It will verify the project and set a new webhook on it to listen for task-level changes.

- _TaskEventHandler/_ - A Lambda function triggered when a task event is received.

- _initializeWebhooks/_ - A Lambda function which is to be run manually. This function is not referenced elsewhere and is meant to be run once to set or re-set webhooks on the artist tracking projects.

- _shared_layer/_ - A Lambda layer that contains shared functions that are used across the Lamda functions

- _template.yaml_ - A template that defines the application's AWS resources and the connections between them.

## Using AWS SAM CLI

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

- SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Python 3 installed](https://www.python.org/downloads/)
- Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

## Configuration

There are several environment variables which the application uses to orient itself and operate on the correct Asana objects. These are defined in the Globals->Function->Environment->Variables of `template.yaml`. Many of these are Global IDs (GID/gid) for specific objects in Asana.

- **ASANA_API_URL**: (eg. "https://app.asana.com/api/1.0/")

  - This is the base URL for the Asana API. If there is ever a major API upgrade and deprectaion, this will be used to define the version of the Asana API. Version changes will be very rare, but are possible in the future. To stay up to date on any changes, follow https://developers.asana.com/docs/news-and-changelog

- **BOT_SECRET_ARN**: !Ref BotSecret

  - This is a reference to the BotSecret resource, which allows the functions to reference the Secrets Manager instance holding webhook secrets and the Asana API key.

- **WORKSPACE_GID**: e.g "6608348560333"

  - This is the GID for the Asana workspace you're working in. 

- **PROJECTS_PORTFOLIO_GID**: e.g. "1201725315313120"

  - This is the GID for the portfolio which contains all tracking projects.