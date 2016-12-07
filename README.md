# exconf

Tool for environment and service specific multi-dimensional configuration.

Exconf provides a structured way to setup your configuration for multi-environment setups
containing services, or other configurable systems, that have common configuration structure but
different environment specific configuration details.

Exconf follows these basic principles:

* Keep it as simple as possible, i.e. it contains minimum set of features that is required.
* The configuration must be easily accessible by basic tools like grep and find.
  This means that grepping for a variable name highlights you every instance of it, period.
* Exconf is designed to be the one place for all your environments configuration, and
  it is kept simplistic for the purpose of clarity on avoiding confusion. Add complexity elsewhere.
