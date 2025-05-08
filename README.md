# Imagen 3 생성 및 편집 기능 실습

# 목표

Imagen 3의 기능을 몇가지 시나리오로 손쉽게 테스트해 봅니다.:

-   Vertex AI Vision AI 콘솔을 이용해 봅니다.
-   텍스트, 이미지, 문서, 음성, 동영상 데이터로 할 수 있는 시나리오를 살펴봅니다.
-   API 레벨에서 몇가지 기능들을 추가로 살펴봅니다.
-   https://github.com/jk1333/image_edit

# Task 1. Vertex AI 에서 Imagen 으로 그림 생성 해보기

Google Cloud 콘솔에서 "imagen" 을 타이핑 하면 나오는 Vision/Vertex AI를 클릭합니다.

아래 화면과 같이 간단하게 그림을 그려봅니다. "마스카라를 바르는 여성의 밝은 스타일 잡지 사진."

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/3/1.png)

# Task 2. Vertex AI의 Imagen API 로 만든 앱 배포 해보기

* Prompt tester를 Cloud Run에 배포

메뉴에서 "cloud run" 을 검색합니다.

상단의 + DEPLOY CONTAINER -> Service 를 클릭합니다

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/1/geminiprompt테스--nsoggf7s2w.png)

Container image URL에는 아래의 내용을 입력합니다.

<table>
  <thead>
    <tr>
      <th><strong>asia-northeast1-docker.pkg.dev/sandbox-373102/education/image_tester:latest</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

나머지 항목은 아래와 같이 설정합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/1/geminiprompt테스--145e81p4nr8.png)

하단의 Container(s), Volumes, Networking, Security 를 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/1/geminiprompt테스--72xld5gz07i.png)

**메모리는 4G를 줍니다.**

하단의 내용을 참고하여 값을 업데이트 합니다.

Request timeout 은 300 -> 3600 으로 업데이트

Execution environment 는 Default -> Second generation 으로 업데이트 합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/1/geminiprompt테스--id68fj4t7w.png)

CREATE 를 클릭합니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/1/geminiprompt테스--vdbsyed3pvi.png)

배포가 완료되면 URL이 활성화 됩니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/1/geminiprompt테스--yvx0jelpy2c.png)

* Image tester 실행

아래와 같이 프롬프트 입력 후 Generate image 버튼을 눌러 동작을 확인합니다.

<table>
  <thead>
    <tr>
      <th><strong>롯데월드에 커플이 놀러가서, 남자는 파란색 체크무늬 셔츠에 갈색 면바지를 입었고, 여자는 녹색 드레스를 입고 밀짚모자를 썼음. 여자는 풍선을 들고 있고, 남자는 솜사탕을 들고 있음. 뒤 배경에는 석촌 호수가 보임. sony DSLR, movie still, warm tones</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/3/2.png)

아래의 샘플들을 통해 몇가지 이미지들을 더 생성해 봅니다.

<table>
  <thead>
    <tr>
      <th><strong>macro photo of a stunning blue bird with red stripes sitting on a blue flower, shiny bird's eye, golden light,  film still</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>Photo of surreal room with everything made from roses flowers, duotone pink and red colors</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>3d city illustration on top of a cloud surrounded by clouds, in the style of cubism-inspired, light teal and light pink, puzzle-like pieces, detailed miniatures</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>hybrid cactus dog, a green dog with cactus spikes instead of fur in the middle of a blurred forest</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>a black and white photo of a tree in a foggy field, featured on unsplash, tonalism, anamorphic widescreen, sun rays from the right</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>macro photo of alien stunning adorable creature sitting on a blue flower, shiny eye, golden light, film still</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>a close up of a figurine of a cute person, a 3D render, candy pastel, walking boy, somber appearance, trending on character design</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>little bee amigurumi on a branch, in the style of light teal and dark sky-blue, selective focus, use of fabric, horizontal stripes</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>black line 'sports car', minimalist geometric line art, simple, vector, white background, centered</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>centered 3-d Letter "B" made from blueberries, studio shot, pastel lavender background</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>Cute pixar style Vector art of a black male, a Korean female , an Indian male with a beard, a sikh man, and a white female with a ponytail, all dancing with their hands up in front of the SF skyline wearing Polo shirts. There are dhols and colorful scarves everywhere. In bold font show "Chuseok!" and in a new line bold font "Fridays 1PM @ Hall" and bold font "http://www.google.com" on the third line.</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>isometric perspective of "house" fully made from "cookie", minimal plain pastel "green" background for product photography, with soft lighting and high focus on the subject.</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th><strong>"Fall is here" written in autumn leaves floating on a lake</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

# Task 3. Gemini 로 프롬프트 생성 후 이미지 생성하기

* 구글 검색을 통해 임의의 이미지를 하나 검색하여 Prompt editor 에 입력하고, 아래와 같은 프롬프트를 통해 Imagen 에서 그리기 위한 프롬프트를 생성해 달라고 요청합니다.

<table>
  <thead>
    <tr>
      <th><strong>위 이미지를 Imagen 으로 그리기 위한 프롬프트를 작성해 주세요.</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

위에서 생성된 프롬프트로 Imagen 을 통해 이미지를 생성해 봅니다.

* 불완전한 이미지 생성 프롬프트를 개선하여 좀더 정확한 이미지를 만들어 봅니다.

<table>
  <thead>
    <tr>
      <th><strong>다음의 내용을 Imagen으로 그리기 위한 프롬프트를 작성해 주세요. "커플이 롯데월드에 놀러간 사진"</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/3/3.png)

# Task 4. Product image 편집 모드 사용하기

* 아래의 프롬프트로 가방을 그려봅니다.

<table>
  <thead>
    <tr>
      <th><strong>에르메스 가방, empty background</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

가방이 그려지면, 마음에 드는 그림을 골라 Edit 버튼을 눌러 편집 모드로 들어갑니다.

편집에 가방에 올라가면, 우측 판넬에서 Edit mode 를 product-image 로 바꾼 후,

Edit Prompt에 아래와 같은 프롬프트를 입력 후 가방을 업데이트 합니다.

<table>
  <thead>
    <tr>
      <th><strong>응접실, 탁자, 화분, 시계, 조명</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/3/4.png)

# Task 5. Outpainting 편집 모드 사용하기

위에서 그린 그림에 대해 Edit 버튼을 클릭하여 편집 모드로 가져옵니다. (혹은 새로 생성해도 됩니다.)

편집에 이미지가 올라가면, 우측 판넬에서 Edit mode를 outpainting 으로 바꾼 후,

Outpaint width 값을 2048 로 수정 후 Edit image 버튼을 누릅니다.

![image](https://raw.githubusercontent.com/jk1333/handson/main/images/3/5.png)

# Task 6. Upscale 사용하기

프롬프트로 예제 이미지를 생성합니다.

<table>
  <thead>
    <tr>
      <th><strong>응접실, 탁자, 화분, 시계, 조명</strong></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>

생성된 이미지에서 선택 박스를 눌러 4096 으로 바꾼 후 Upscale 버튼을 누릅니다.

Upscale 후 Download 버튼을 눌러 결과물을 확인합니다.