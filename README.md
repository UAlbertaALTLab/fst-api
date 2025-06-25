# Docker configuration for FST_API

To deploy this docker image, you must have a `.env` file with the following variables:
- `FST_API_FST_PATH`: (required) The path where the FSTs are stored in the machine hosting the docker image.  It is necessary for making the FSTs available inside the docker image.
- `FST_API_ANALYSER_FST`: (optional) The filename of the analyser FST (with extension, without path). If missing, it defaults to "analyser.hfstol"
- `FST_API_GENERATOR_FST`: (optional) The filename of the generator FST (with extension, without path). If missing, it defaults to "generator.hfstol"

If you intend to expose the API on the Internet instead of just using it locally, you should add to the `.env` file the allowed host names, for example:

    FST_API_ALLOWED_HOSTS=ciw-api.altlab.dev
