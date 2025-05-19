### Part 1: Enhancing the Classifier

- What are the limitations in the current classifier that's stopping it from scaling?

1. _The classifier is only able to classify files based on their filenames and not the contents of the file. This is a problem when filenames are not descriptive or not consistent._
2. _The classifier is limited to the file types that are currently supported. This is a problem when we want to classify files from new industries._
3. _The classifier can only process one file at a time. This is a problem when we want to classify large volumes of files._

- How might you extend the classifier with additional technologies, capabilities, or features?

1. _We can use a pre-trained model to classify the file contents or we can use a custom model to classify the file contents for specific industries or use cases._
2. _We can use a multi-modal model to classify the file by combining the text-based name, image/contents of the file, and any metadata that is available._
3. _We can use a model that is able to understand a long tail of potentially niche file formats for a variety of industries._

### Part 2: Productionising the Classifier 

- How can you ensure the classifier is robust and reliable in a production environment?

1. _We can write LLM Evals into our test suite to ensure that the classifier is robust and reliable._
2. _We can allow the API to accept a list of files and process them in batch._
3. _We can implement a rate limiting layer to ensure that the classifier is not overwhelmed by requests._
4. _We can implement a logging layer to ensure that the classifier is not overwhelmed by requests._

- How can you deploy the classifier to make it accessible to other services and users?
1. _We can deploy the classifier to a cloud platform such as AWS, GCP, or Azure._
2. _We can use a serverless architecture to deploy the classifier. eg. AWS API Gateway_
3. _We can implement an authentication layer with JWT tokens to ensure that only authorized users can access the classifier._
4. _We can write clear documentation on how to use the classifier, including authentication & rate limit details and how to use the API._
