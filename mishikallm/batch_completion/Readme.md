# Implementation of `mishikallm.batch_completion`, `mishikallm.batch_completion_models`, `mishikallm.batch_completion_models_all_responses`

Doc: https://docs.21t.cc/docs/completion/batching


MishikaLLM Python SDK allows you to:
1. `mishikallm.batch_completion` Batch mishikallm.completion function for a given model.
2. `mishikallm.batch_completion_models` Send a request to multiple language models concurrently and return the response
    as soon as one of the models responds.
3. `mishikallm.batch_completion_models_all_responses` Send a request to multiple language models concurrently and return a list of responses
    from all models that respond.