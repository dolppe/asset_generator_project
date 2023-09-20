# asset-generator

[![Lint Code Base](https://github.com/dolppe/asset_generator_project/actions/workflows/linter.yml/badge.svg)](https://github.com/dolppe/asset_generator_project/actions/workflows/linter.yml)

달콤소프트 기획팀에서 제작하는 기획서 엑셀파일을 GMTOOL에 업로드하는 에셋엑셀 파일로 변환하는 프로그램.

## Structure

<details>
    <summary>프로젝트 구조 살펴보기</summary>

```sh
asset-generator
 ┣ .github
 ┃ ┗ workflows            -> workflows 설정
 ┃ ┃ ┗ linter.yml         -> linter 설정
 ┣ output                 -> 결과물 저장 위치
 ┃ ┗ .gitignore
 ┣ resources              -> 실행에 사용되는 리소스
 ┃ ┗ input                -> 입력시 사용되는 리소스
 ┃ ┃ ┣ base               -> 기존 에셋 엑셀
 ┃ ┃ ┃ ┗ ...
 ┃ ┃ ┣ mapping.xlsx       -> 매핑 데이터
 ┃ ┃ ┗ planning.xlsx      -> 기획서
 ┣ asset_generator        -> 패키지
 ┃ ┣ generate             -> 시트 생성과 관련된 서브 패키지
 ┃ ┃ ┣ group.py           -> 그룹 처리 모듈
 ┃ ┃ ┣ theme.py           -> 테마 처리 모듈
 ┃ ┃ ┣ music.py           -> 음악 처리 모듈
 ┃ ┃ ┣ store.py           -> 상점 처리 모듈
 ┃ ┃ ┣ packaging.py       -> 패키징 처리 모듈
 ┃ ┃ ┣ item.py            -> 아이템 처리 모듈
 ┃ ┃ ┣ background.py      -> 배경 처리 모듈
 ┃ ┃ ┗ mission.py         -> 미션 처리 모듈
 ┃ ┣ preprocess           -> 전처리와 관련된 서브 패키지
 ┃ ┃ ┣ input_combine.py   -> 입력 데이터 전처리 모듈
 ┃ ┃ ┣ group_transfer.py  -> 그룹 이전 모듈
 ┃ ┃ ┗ store_arrange.py   -> 상점 기간 전처리 모듈
 ┃ ┣ main.py              -> 모듈 순차 실행
 ┃ ┗ utils.py             -> 전역에서 사용되는 로직
 ┣ tests                  -> 테스트 : 패키지 내부 및 리소스에 동일한 구조
 ┃ ┣ generate
 ┃ ┃ ┣ test_background.py
 ┃ ┃ ┣ test_group.py
 ┃ ┃ ┣ test_item.py
 ┃ ┃ ┣ test_mission.py
 ┃ ┃ ┣ test_music.py
 ┃ ┃ ┣ test_packaging.py
 ┃ ┃ ┣ test_store.py
 ┃ ┃ ┗ test_theme.py
 ┃ ┣ preprocess
 ┃ ┃ ┣ test_group_transfer.py
 ┃ ┃ ┣ test_input_combine.py
 ┃ ┃ ┗ test_store_arrange.py
 ┃ ┣ resources
 ┃ ┃ ┗ input
 ┃ ┃ ┃ ┣ base
 ┃ ┃ ┃ ┃ ┗ ...
 ┃ ┃ ┃ ┣ test_mapping.xlsx
 ┃ ┃ ┃ ┗ test_planning.xlsx
 ┃ ┣ context.py
 ┃ ┣ test_main.py
 ┃ ┗ test_utils.py
 ┣ .flake8                -> flake8 설정
 ┣ .gitignore
 ┣ .pre-commit-config.yaml-> pre-commit
 ┣ .pylintrc              -> pylint 설정
 ┣ .pyproject.toml        -> black 설정
 ┣ README.md
 ┗ requirements.txt
```

</details>

## Requirements

- Python 3.9.7

## Install

<details>
    <summary>프로젝트 설치 과정 설명</summary>

### 1. Python 3.9.7 설치 파일을 다운로드합니다.

[설치 파일 다운로드 페이지 가기](https://www.python.org/downloads/release/python-397/)  
 해당 링크 아래쪽에 있는 Files에서 운영체제에 맞는 파일을 설치 합니다.  
 Windows => Windows installer (64-bit) / Windows installer (32-bit)

![파이썬 설치](https://user-images.githubusercontent.com/112839327/221080426-60f25fc3-15e9-4a08-bb90-d0007e14b83c.png)

### 2. Python 설치를 진행 합니다.

다운로드 받은 Python 설치 파일을 실행 시킵니다.  
 아래 사진과 같이 Add Python 3.9 to PATH에 체크한 후에 Install Now를 누릅니다.

![패스추가](https://user-images.githubusercontent.com/112839327/221082144-2abacbcb-29d0-4242-87fb-378bc68baa11.png)  
 자동으로 Python 설치가 진행됩니다.

### 3. Python 설치를 확인 합니다.

명령 프롬프트(cmd)를 열어서 아래 명령어를 입력하여 Python 버전을 확인합니다.

[명령 프롬프트(cmd) 여는 방법 for Windows](https://ko.wikihow.com/%EC%9C%88%EB%8F%84%EC%9A%B0%EC%A6%88%EC%97%90%EC%84%9C-%EB%AA%85%EB%A0%B9-%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%EB%A5%BC-%EC%97%AC%EB%8A%94-%EB%B0%A9%EB%B2%95)

(실행을 포함한 아래 설명의 모든 명령은 cmd에서 진행합니다.)

```sh
python --version
```

아래와 같이 Python 3.9.7이라는 결과가 나오면 설치가 완료된 것입니다.

![파이썬 설치 확인](https://user-images.githubusercontent.com/112839327/221082608-b0ca4553-c102-40c0-bc89-5d1eec9872a5.png)

### 4. Git 설치 파일을 다운로드합니다.

[Git 설치 파일 다운로드 페이지 가기](https://git-scm.com/download/win)  
 버전에 맞는 파일을 선택합니다.

![깃다운로드](https://user-images.githubusercontent.com/112839327/221146636-eddd194c-877c-4ec6-a9f8-7abe7199ad04.png)

### 5. 다운로드 받은 파일을 실행하여 Git을 설치 합니다.

추가적인 선택 없이 Next를 계속 눌러 설치를 진행합니다.

![깃설치](https://user-images.githubusercontent.com/112839327/221147149-88e92136-8ad0-4ac0-a290-329f90fbf013.png)

### 6. asset-generator 프로젝트 설치를 진행합니다.

```sh
cd Desktop
git clone https://github.com/dolppe/asset_generator_project.git
```

아래와 같은 창이 뜨면 Sign in with your browser를 선택합니다.

![깃허브 로그인](https://user-images.githubusercontent.com/112839327/221146647-982a4436-f533-4282-b3a4-ca4840872c8a.png)  
 이후, 회사 계정으로 깃허브 로그인을 진행합니다.  
 로그인을 완료하면 자동으로 프로젝트의 설치가 진행됩니다.

![깃허브 로그인 브라우저](https://user-images.githubusercontent.com/112839327/221146642-1bb454c0-0c8c-4b59-b533-1bac02a42d3d.png)

### 7. 필요한 파이썬 패키지를 설치합니다.

```sh
cd asset-generator
pip install -r requirements.txt
```

</details>

## Usage

- 프로젝트를 실행 시킵니다.

  미리 설정된 리소스를 사용하고자 하는 경우 (동작 테스트)

  ```sh
  python asset_generator/main.py
  ```

  리소스를 새로 설정하고자 하는 경우

  띄어쓰기를 기준으로 필요한 파일의 경로를 입력합니다.

  ```sh
  python asset_generator/main.py [기존에셋엑셀 파일경로] [planning 파일경로] [mapping 파일경로] [결과물 파일경로]
  ```

  예시 :

  상대경로를 이용하는 경우

  ```sh
  python asset_generator/main.py resources/input/base/SSY_Live_3.7.26_230209.xlsx resources/input/planning_0216.xlsx resources/input/mapping.xlsx output/output.xlsx
  ```

  또는

  절대경로를 이용하는 경우

  ```sh
  python asset_generator/main.py /Users/yeonjilim/Documents/GitHub/dalcom/asset-generator/resources/input/base/SSY_Live_3.7.26_230209.xlsx /Users/yeonjilim/Documents/GitHub/dalcom/asset-generator/resources/input/planning_0216.xlsx /Users/yeonjilim/Documents/GitHub/dalcom/asset-generator/resources/input/mapping.xlsx /Users/yeonjilim/Documents/GitHub/dalcom/asset-generator/output/output.xlsx
  ```

### 기존 에셋 엑셀 (입력 데이터)

이전 라이브 업데이트의 에셋 엑셀입니다.

### Planning (입력 데이터)

이번 업데이트에 대한 내용을 적습니다.

**고려사항**

<details>
    <summary>미션 영역 작성하기</summary>

기존 기획서의 미션 부분을 복사, 붙여넣기합니다.

1. 기획서의 미션 영역을 선택합니다.

   <img width="1238" alt="image" src="https://user-images.githubusercontent.com/112838998/221746032-f9c41365-374d-4786-86e3-4d938444442b.png">

2. 엑셀 홈 > 병합하고 가운데 맞춤 > 셀 분할

   <img width="811" alt="image" src="https://user-images.githubusercontent.com/112838998/221746185-9a775a82-4214-41ed-b5f1-46c48372aefa.png">

   셀 분할이 된 모습

   <img width="1249" alt="image" src="https://user-images.githubusercontent.com/112838998/221746271-af99491d-754d-44fe-b9cd-3a983de7dab3.png">

3. 미션 내용을 복사 후 붙여넣습니다.

   복사 영역

   <img width="1239" alt="image" src="https://user-images.githubusercontent.com/112838998/221746409-5926e58a-1b6e-49bb-99c1-e32ab12e59c1.png">

   **주의!!** 미션 보상 아이템명과 상점 메뉴명에 오타가 있어서는 안됩니다.

4. 하단에 conditionScript 영역에서 각 미션에 맞는 conditionScript 값을 채웁니다.(필요없는 값은 채우지 않아도 됩니다.)

</details>

### Mapping (입력 데이터)

해당 프로젝트에 적용되는 값들을 적습니다.

각 프로젝트당 하나의 Mapping이 존재합니다.

최초에 한번 작성되고 나면 그 이후에는 새로운 그룹이나 앨범이 추가되는 경우에만 수정합니다.

### 결과물 관련 사항

엑셀의 서식이 모두 지워집니다. (색상, 테두리)

## Lint

pep8을 준수하기 위해 [pylint](https://pylint.pycqa.org/en/latest/), [flake8](https://flake8.pycqa.org/en/latest/index.html#), [black](https://black.readthedocs.io/en/stable/index.html)을 사용하고 있습니다.

작업한 파일의 준수 여부는 pull request 시 체크 됩니다.

commit 시 준수 여부 체크 자동화를 설정하려면 clone 후 다음 명령을 실행하면 됩니다.

```sh
pre-commit install
```
