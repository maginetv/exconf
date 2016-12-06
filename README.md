# exconf

Tool for environment and service specific multi-dimensional configuration.

Exconf provides a structured way to setup your configuration for multi-environment setups
containing services, or configurable systems, that have common configuration structure but
different environment specific configuration details.

The basic idea is that you configure your service in YAML format and have some executable deployment
or other type of scripts that you want to call for the service with varying configuration.
The configuration structure can be written per service and the variables in the configuration
recursively replaced by the environment specific variables. This gives you a common way to call
the executables for the services, and you will get well defined environment, service, and deployment
specific configuration for the execute script.

The executables can be different deployment triggering calls, like for some service scheduler, or
some other configuration management tool, like Ansible. The idea is to have all the configuration in
one structured configuration repository, while the types of deployments or other typed of executions
can vary per environment.

Everything is configurable by you, and the basic case is extremely simple, but you can setup it
as complex as you need to. Next let's look into few examples.
