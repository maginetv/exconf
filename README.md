# exconf

Tool for environment and service specific multi-dimensional configuration.

Exconf provides a structured way to setup your configuration for multi-environment setups
containing services, or other configurable systems, that have common configuration structure but
different environment specific configuration details.

Exconf follows these basic principles:

* Keep it as simple as possible, i.e. it contains minimum set of features that is required,
  and more complex templating features like includes and loops are outside the scope of Exconf.
* The configuration must be easily accessible by basic tools like grep and find.
  This means that grepping for a variable name highlights every instance of it, and no
  templating magic will hide it.
* Exconf is designed to be the one place for all your environments configuration, and
  it is kept simplistic for the purpose of clarity and avoiding confusion. Add complexity elsewhere,
  like trigger an *Ansible* playbook or whatever other configuration management tool for
  more complex needs.


## Install Exconf

Clone the source repository and build a Debian package or Python egg/wheel by calling any of:

```
make egg
```

```
make wheel
```

```
make deb
```

You can also just install the Python package locally by:

```
make install
```

Exconf source is compatible with Python 2.7 and Python 3.5 or later.


## Hello-World Example

After you have installed exconf CLI, and you just want to try out the basic functionality, you can
point the tool into the "example" configuration space within the exconf source code. Assuming here
that the source code lives in directory */code/exconf*. Try out the following calls:

```
exconf --help
```

```
exconf -c /code/exconf/example list-services
```

```
exconf -c /code/exconf/example list-envs
```

You can also define an environment variable `EXCONF_CONFIG_ROOT` so you don't need to give the `-c`
flag every time.

```
export EXCONF_CONFIG_ROOT=/code/exconf/example
```

Now you should be able to do just:

```
exconf list-services
```

There is only one simplistic *hello-world* service available in example directory. Try out to get
configurations for *hello-world*, and also executing the defined template type executable, which is
just plan echo command in this case, printing out a configured text message into stdout.

```
exconf variables -s hello-world -e local
```

```
exconf template -s hello-world -e local
```

```
exconf execute -s hello-world -e local
```

Continue reading to learn what all of the calls actually mean.


## Exconf Overview

Things you will need to setup:
* Exconf command line (CLI) tool for populating templates and executing scripts on configurations.
* Configuration root folder on your host, which you probably want to version control for
  persistency and version history.

Configuration folder contains:
* **exconf.yaml** containing the generic configuration for the Exconf tool.
* **templates** directory for your service configuration templates.
* **environments** directory for your environment specific configuration variables.
* **services** directory for your service specific configuration variables.

NOTICE: You can change the name of these directories in the *exconf.yaml*, if you wish.

NOTICE: Variables "service" and "environment" are set into the variables automatically,
        when you populate the templates or list variables, based on the CLI input.

CLI supports following commands:
* **"execute"** a script, which is usually for deployment purposes for a service. The execution must
  always target some service and some environment defined in the configuration folder.
* **"template"** command prints out the templates for your service without executing any scripts.
  You usually use this for confirming you configuration is valid before executing a deployment.
  You can also just write out the templates into chosen directory using the *-w* flag.
* **"variables"** command can be used to print out all the variables that can be applied to the
  targeted service and environment.

Exconf supports **recursive resolution** of the configuration variables used within the
configuration templates. When you use Exconf string templates in your configurations, Exconf
will replace the string templates with configuration variables defined in the *environments*
and *services* folders. Variables inside other variables will be replaced in recursive manner
until all string templates are resolved.

When you call *execute* or *template* command, the CLI will generate a temporary folder
locally and copy all the templates defined in the *templates* folder for your specific
*template_type* that is defined for the service and environment. These templates will be resolved
and all found string variables replaced by the recursively resolved variables as described above.
Finally, if you called *execute*, the *execution_command* will be executed, as defined in
the variables. The default value for *execution_command* is defined in *exconf.yaml*, but you can
overwrite this as any other variable.


### The variable resolving and overwrite order

1. *exconf.yaml*
2. *environments*/*.yaml
3. *environments*/\<target_environment\>/*.yaml
4. *services*/\<target_service\>/*.yaml
5. *environments*/\<target_environment\>/*services*/\<target_service\>/*.yaml
6. CLI parameter overrides

Notice the the structure above is static and defines the structure for your configuration folder.
You don't need to define all the levels mentioned above, and the CLI will just skip folders or
configurations it cannot find.

The structure for the configuration folder allows you to define service and environment specific
configurations, and also different configurations for a specific service only on specific
environment. This can be rephrased as:
* *environments* folder contains configurations for all services in all environments.
* *environments*/\<target_environment\> folder contains configurations for all services on
  a specific environment.
* *services*/\<target_service\> folder contains configurations for specific service
  in all environments.
* *environments*/\<target_environment\>/*services*/\<target_service\> folder contains configurations
  for specific service in a specific environment.

If there are multiple YAML files in a folder to be resolved, they will be applied in alphabetical
order. For example, you might have *environments/defaults.yaml* and *environments/globals.yaml*,
in which case the conflicting variables defined in *defaults.yaml* will be overwritten
by the equally named variables in *globals.yaml*.


### The templates resolving and overwrite order

1. *templates*/\<template_type\>/*
2. *templates*/\<template_type\>/*environments*/\<target_environment\>/*
3. *templates*/\<template_type\>/*services*/\<target_service\>/*
4. *templates*/\<template_type\>/*environments*/\<target_environment\>/*services*/\<target_service\>/*

Notice again that you do not need to define all of these sub-folders for your templates, and usually
you are fine with just the *template_type* root level configurations that apply similarly to all
services in any environment using the type of template.

If the same configuration file name is defined in lower levels, the higher level template will be
overwritten by the more specific configuration.

Try out the configuration resolution using the CLI **template** command.


### File name string templates

Some systems require the configuration file names to be specific, like the name of the service
being deployed. For this purpose you can use file name string templates, which have separately
defined string template prefix and suffix in the *exconf.yaml*. The default is three underscores,
i.e. "___", for prefix and suffix.

As an example let's say that you would need to have a configuration file named after the deployed
service name with .yml file type extension, you could add a file named *\_\_\_service\_\_\_.yml*
into the templates directory for the *template_type* your service is using. If your service
is named *my_service*, when populating the templates, the file would become *my_service.yml*
in the work directory created for execution.
