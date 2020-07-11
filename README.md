# Kodeveploper Blog

### [View Live Kodeveloper Blog &rarr;](https://kodeveloper.com)

![](/img/blog-desktop.png)

## Prepare

- Download and Install [Docker For Mac](https://store.docker.com/editions/community/docker-ce-desktop-mac)

## Quick Start

```bash
$ git clone https://github.com/kodevops/blog.git $HOME/kodevops/blog && cd $HOME/kodevops/blog
$ docker run -it -p 4000:4000 -v $HOME/kodevops/blog:/srv/jekyll --name kodevops-blog jekyll/jekyll bash

# Guest
$ bundle update
$ exit

# Host
$ docker start kodevops-blog
$ docker exec -it kodevops-blog jekyll serve

# Open your browser
http://localhost:4000
or http://192.168.99.100:4000
```

## Clean Up

```bash
$ docker rm kodevops-blog
$ docker rmi jekyll/jekyll
```

## Docs

Move to [docs](/docs/README.md)

## License

Apache License 2.0.
Copyright (c) 2018 Kodeveloper
https://github.com/Huxpro/huxpro.github.io
Kodeveloper Blog is derived from [Hux Blog (Apache License 2.0)](https://github.com/Huxpro/huxpro.github.io) Copyright (c) 2015-2016 Huxpro and [Clean Blog Jekyll Theme (MIT License)](https://github.com/BlackrockDigital/startbootstrap-clean-blog-jekyll/)
Copyright (c) 2013-2016 Blackrock Digital LLC.
