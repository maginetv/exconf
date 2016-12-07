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


## Exconf Overview

Things you will need to setup:
* Exconf command line (CLI) tool for templating and executing your configurations.
* Configuration root folder on your host, which you probably want to version control for real use.

Configuration folder will contain:
* *exconf.yaml* containing the generic configuration for the Exconf tool.
* *templates* directory for your service configurations.
* *environments* directory for your environment specific configuration variables.
* *services* directory for your service specific configuration variables.

NOTICE: You can change the name of these directories in the *exconf.yaml*, if you wish.

The actions the CLI supports for the configurations:
* **"execute"** a script, which is usually for deployment purposes for a service. The execution must
  always target some service and some environment defined in the configuration folder.
* **"template"** command prints out the templates for your service without executing any scripts.
  You usually use this for confirming you configuration is valid before executing a deployment.
* **"variables"** command can be used to print out all the variables that can be applied to the
  targeted service and environment.

Exconf supports **recursive resolution** of the configuration variables used within the
configuration templates. When you use Exconf string templates in your configurations, Exconf
will replace the string templates with configuration variables defined in the *environments*
and *services* folders. Variables inside other variables will be replaced in recursive manner
until all string templates are resolved.

When you call *execute* or *template*, the CLI will generate a temporary folder
locally and copy all the templates defined in the *templates* folder for your specific
*template_type* that is defined for the service and environment. These templates will be resolved
and all found string variables replaced by the recursively resolved variables as described above.
Finally, if you called *execute*, the *execution_command* will be executed, as defined in
the variables. The default value for *execution_command* is defined in *exconf.yaml*, but you can
overwrite this as any other variable.

The variable resolving and overwrite order:
1. *exconf.yaml*
2. *environments*/*.yaml
3. *environments*/<target_environment>/*.yaml
4. *services*/<target_service>/*.yaml
5. *environments*/<target_environment>/*services*/<target_service>/*.yaml
6. CLI parameter overrides


If there are multiple YAML files in a folder to be resolved, they will be applied in alphabetical
order. For example, you might have *environments/defaults.yaml* and *environments/globals.yaml*,
in which case the conflicting variables defined in *defaults.yaml* will be overwritten
by *globals.yaml*.


## Hello World Example

You define your configuration in the *templates/<template_type>/my_config.yaml*, and for execution
you might have a script in *templates/<template_type>/deploy.sh*. The default execution script
is defined also in *exconf.yaml*, and initially it is *deploy.sh*. When you call the CLI for
execution, this is how it finds the file to execute.

1. Install exconf from a Debian package, or run it directly from the source.

2. Initialize new configuration source location.

TODO: keep working here
