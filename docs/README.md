# Docs

현재 저희 블로그는 [jekyll](https://jekyllrb.com/)를 기반으로 사용하며, [Hux Blog](https://github.com/Huxpro/huxpro.github.io)의 테마를 수정해서 블로그를 관리 및 운영 하고 있습니다. 그에따라 어떻게 수정하고 관리할건지에 대해 정리한 도큐멘트 입니다.

## 목차

- 디렉토리 구조
- 환경 구축하기
- 워크 프로세스
- 시작 하기
- 디플로이

## 디렉토리 구조

상세한 사항은 공식 홈페이지에 [디렉토리 구조](https://jekyllrb-ko.github.io/docs/structure/) 라는 주제로 자세히 설명 되어있습니다.

자주 쓰는 파일 및 폴더는 아래와 같습니다.

```
_config.yml: 환경설정 파일
_layouts: 페이지의 전체적인 템플릿
_includes: 재사용하기 위한 컴포넌트
_includes/about/ko: /about에 대한 markdown
_posts: 고군분투기등 컨텐츠를 작성
staff: 운영진 정보
_site: 위의 정보를 바탕으로 빌드된 최종 결과물
```

## 환경 구축하기

- Mac

    1. [Docker For Mac](https://store.docker.com/editions/community/docker-ce-desktop-mac)를 다운로드

    2. [레포지토리](https://github.com/kodevops/blog)를 다운로드

        디렉토리 구조는 마음대로 하셔도 상관없습니다만 `에러`를 줄이고 싶은분은 그대로 따라 해주세요.

        ```
        # 사전에 $HOME/kodevops를 생성할 필요가 있습니다.(mkdir $HOME/kodevops)
        $ git clone https://github.com/kodevops/blog.git $HOME/kodevops/blog && cd $HOME/kodevops/blog
        ```

    3. Docker 실행하기

        ```
        # 아래의 명령어로 이미지 다운로드, 컨테이너 생성, 컨테이너에 접속까지 진행 됩니다.
        $ docker run -it -p 4000:4000 -v $HOME/kodevops/blog:/srv/jekyll --name kodevops-blog jekyll/jekyll bash

        # Guest환경(도커)에서 아래의 명령어를 실행합니다.
        $ bundle update
        $ exit

        # Host환경에서 아래의 명령어를 통해서 서버를 실행 시킵니다.
        $ docker start kodevops-blog
        $ docker exec -it kodevops-blog jekyll serve
        ```

    4. 페이지 확인하기

        ```
        # Open your browser
        http://localhost:4000
        http://192.168.99.100:4000
        ```

- Windows
    윈도우즈 환경에서 구축하신 경험이 있으신분은 `PR` 부탁 드립니다 :)

### 워크 프로세스

기본적인 `워크 프로세스`


1. 작업할 폴더에 이동해서 작업을 한다.

2. jekyll를 빌드 및 실행 한다.
    ```
    # 빌드 + 실행
    $ jekyll serve
    ```

3. 빌드가 성공 되면, `__site` 폴더가 만들어지며, 서버가 `__site` 폴더를 root로 실행된다.

4. 브라우저로 확인

5. 반복


### 시작 하기

간단하게 몇가지 예를 들어서 설명 하도록 하겠습니다.
이정도만 기억하시면, 다른건 문제 없이 진행할수 있을거라 생각합니다.

- 고군분투기 작성하기
- 운영진 프로필 수정하기

#### 고군분투기 작성하기

`_posts`폴더안에 컨텐츠를 작성할 필요가 있습니다.(e.g:  ./_posts/2016-08-14-struggle-1.markdown)

1. `_posts` 폴더로 이동해서 미리 작성된 마커다운을 복사합니다.

    ```
    $ cp ./_posts/xxx.markdown ./_posts/zzz.markdown
    ```

2. 컨텐츠의 내용물을 변경한뒤 저장합니다.

3. 서버를 실행 시킵니다.

    ```
    $ docker exec -it kodevops-blog jekyll serve
    ```
4. 브라우저로 페이지 확인합니다.

    ```
    # Open your browser
    http://localhost:4000
    http://192.168.99.100:4000
    ```

#### 운영진 프로필 수정하기

1. 미리 작성된 `./staff/index.html`를 수정 한뒤 저장합니다.

2. 서버를 실행 시킵니다.

    ```
    $ docker exec -it kodevops-blog jekyll serve
    ```
3. 브라우저로 페이지 확인합니다.

    ```
    # Open your browser
    http://localhost:4000
    http://192.168.99.100:4000
    ```

### 디플로이

`Master` 브랜치에 `Push`하시면 자동으로 [블로그](https://kodeveloper.com)에 디플로이가 됩니다.

#### 프로세스

레포지토리
- 블로그 원본파일의 레포지토리를 `A레포지토리`라고 함.
    [kodevops/blog](https://github.com/kodevops/blog)
- 생성된 정적파일의 레포지토리를 `B레포지토리`라고 함.
    [kodevops/kodevops.github.io](https://github.com/kodevops/kodevops.github.io)


1. `A레포지토리` Master브랜치에 Push
2. `A레포지토리` Master브랜치가 갱신되었을 경우 Travis CI가 실행됨.
    2-1. jekyll 빌드
    2-2. `B레포지토리`의 소스코드 다운로드
    2-3. 빌드된 결과물을 `B레포지토리`에 복사
    2-4. `B레포지토리` Master브랜치에 Push
3. 디플로이 완료
