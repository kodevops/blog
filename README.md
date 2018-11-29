# Kodeveploper Blog

### [View Live Kodeveloper Blog &rarr;](https://kodeveloper.com)

![](https://kodeveloper.com/img/blog-desktop.png)


## Prepare

- [Docker For Mac](https://store.docker.com/editions/community/docker-ce-desktop-mac)

## Use

```
$ git clone https://github.com/kodevops/kodevops.git $HOME/jekyll
$ docker run -it -p 4000:4000 -v $HOME/jekyll:/srv/jekyll --name jekyll jekyll/jekyll bash

# Guest
$ bundle update
$ exit

$ docker start jekyll
$ docker exec -it jekyll jekyll serve

# Open your browser
http://localhost:4000
or http://192.168.99.100:4000
```

## License

Apache License 2.0.
Copyright (c) 2018 Kodeveloper
https://github.com/Huxpro/huxpro.github.io
Kodeveloper Blog is derived from [Hux Blog (Apache License 2.0)](https://github.com/Huxpro/huxpro.github.io) Copyright (c) 2015-2016 Huxpro and [Clean Blog Jekyll Theme (MIT License)](https://github.com/BlackrockDigital/startbootstrap-clean-blog-jekyll/)
Copyright (c) 2013-2016 Blackrock Digital LLC.
