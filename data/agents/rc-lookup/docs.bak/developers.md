---
layout: docs
title: Developers
permalink: docs/developers/
---
## Running locally

### Prerequisite docker

- Setting up your dev environment for the first time:
    ```
    docker run -p 127.0.0.1:9042:9042 --name m_cassandra -d cassandra:3.0.9
    docker run -p 127.0.0.1:2181:2181 --name m_zookeeper -d zookeeper:latest
    ```
- Once the two docker images are built, whenever you stop and start docker (especially on Mac, as Docker is an app), you'll need to run these two commands instead:
  ```bash
  docker restart m_cassandra
  docker restart m_zookeeper
  ```

### Running migration and keyspaces

```sh
sbt createKeyspace
sbt migrate
sbt "project rule-admin" createKeyspaces
```

### Seeding database with initial data

#### Currently available Seeds
1. `BaseSeed.scala` : Domain/ActionMap(PASS,BLOCK)/Username

```sh
sbt "project maquette-seeds" run
```

### Building and running within Intellij
You should run correct application class in Intellij, for example com.paytmlabs.maquette.ruleadmin.Application in case of rule-admin.
Add to the VM Options in the Run Configuration, replacing the url with your url and the correct project:

```sh
-Dconfig.url=file:$WORKSPACE_DIR/maquette/rule-admin/src/main/resources/application.conf
```


### Building and running rule-admin

```sh
sbt "project rule-admin" docker:publishLocal
./docker/rule-admin/run_local.sh
```
You need to create at least one domain in cassandra rt_engine database:
```sh
$ docker exec -it m_cassandra cqlsh
Connected to Test Cluster at 127.0.0.1:9042.
[cqlsh 5.0.1 | Cassandra 3.0.9 | CQL spec 3.4.0 | Native protocol v4]
Use HELP for help.
cqlsh> use rt_engine;
cqlsh:rt_engine> INSERT INTO domain(name) VALUES('BANKING');
```

Check if application is running at http://127.0.0.1:8083/version

You can now try to access REST endpoints that require authentication, for example: http://127.0.0.1:8083/v1/risklist. Local config does not really check passwords, so you can supply "super-admin" as a username with any password or no password at all.

#### Running rule-admin UI
The UI for rule-admin is a separate project: https://bitbucket.org/paytmteam/maquette-admin-ui/


### Building and running rule-engine

```sh
sbt "project rule-engine" docker:publishLocal
./docker/rule-engine/run_local.sh
```

### Building the Documentation

```sh
gem install jekyll
sbt "project site" clean update makeMicrosite
cd site/target/jekyll
jekyll serve
```

Open browser to localhost:4000

## Configure pre-commit hook (optional/recommended)

A pre-commit hook is available to validate that your code compiles and is properly formatted by scalafmt.

``sh
./hook/pre-commit-hook-install.sh
``

NOTE: This script is designed for Mac and installs scalafmt using brew. If you're not on Mac (say, Linux), you have to [install scalafmt](https://scalameta.org/scalafmt/docs/installation.html) yourself.
