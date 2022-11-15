from neuralintents import GenericAssistant
import nltk
nltk.download('omw-1.4')
chatbot = GenericAssistant("intents.json")
chatbot.train_model()
chatbot.save_model(model_name='jacob1.0')