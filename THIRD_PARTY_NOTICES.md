# Third-party notices

## Base model

The default base model is Qwen/Qwen3-0.6B, provided by the Qwen team under the Apache License
2.0. The default configuration pins revision
`c1899de289a04d12100db370d81485cdf75e47ca`. Its license is available at:

https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/LICENSE

The base model is not included in this source repository. A release operator must preserve
all notices required by the base-model license and re-verify the model card and license for
the exact downloaded revision before publishing derived weights. The release pipeline
downloads that exact license, verifies its configured SHA-256 digest, and packages it as
`BASE_MODEL_LICENSE.txt`.

## Training data

The bundled MQDeck AI training data is original project content released under the MIT
license in `DATASET_LICENSE`. No IBM documentation, IBM software, website corpus, customer
data, or third-party operational content is included.
