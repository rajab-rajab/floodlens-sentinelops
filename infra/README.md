# FloodLens AWS backend
CDK stack: private encrypted S3 evidence bucket, HTTP API, encrypted SQS queue with DLQ, submission Lambda, and a placeholder worker. Configure AWS credentials, set a USD 1 budget alert, run `npm install`, `npx cdk bootstrap`, `npm run synth`, then `npx cdk deploy -c allowedOrigin=https://your-site.example`. No resources have been deployed by this repository.
