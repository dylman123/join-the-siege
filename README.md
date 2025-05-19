### Part 1: Enhancing the Classifier

- What are the limitations in the current classifier that's stopping it from scaling?
_There are a few limitations in the current classifier that's stopping it from scaling:_

_1. The classifier is only able to classify files based on their filenames and not the contents of the file. This is a problem when filenames are not descriptive or not consistent._
_2. The classifier is limited to the file types that are currently supported. This is a problem when we want to classify files from new industries._
_3. The classifier can only process one file at a time. This is a problem when we want to classify large volumes of files._

- How might you extend the classifier with additional technologies, capabilities, or features?

_1. We can use a pre-trained model to classify the file contents or we can use a custom model to classify the file contents for specific industries or use cases._
_2. We can use a multi-modal model to classify the file by combining the text-based name, image/contents of the file, and any metadata that is available._
_3. We can use a model that is able to understand a long tail of potentially niche file formats for a variety of industries._


### Part 2: Productionising the Classifier 

- How can you ensure the classifier is robust and reliable in a production environment?

_1. We can write LLM Evals into our test suite to ensure that the classifier is robust and reliable._
_2. We can allow the API to accept a list of files and process them in batch._
_3. We can implement a rate limiting layer to ensure that the classifier is not overwhelmed by requests._
_4. We can implement a logging layer to ensure that the classifier is not overwhelmed by requests._

- How can you deploy the classifier to make it accessible to other services and users?
_1. We can deploy the classifier to a cloud platform such as AWS, GCP, or Azure._
_2. We can use a serverless architecture to deploy the classifier. eg. AWS API Gateway_
_3. We can implement an authentication layer with JWT tokens to ensure that only authorized users can access the classifier._
_4. We can write clear documentation on how to use the classifier, including authentication & rate limit details and how to use the API._
