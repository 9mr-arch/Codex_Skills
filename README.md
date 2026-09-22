# Codex 제작 스킬 모음

## 가장 쉬운 설치: Codex에 아래 문장 붙여 넣기

로컬 파일을 다룰 수 있는 Codex 앱이나 CLI의 새 대화에서 아래를 그대로 요청하세요.

```text
https://github.com/9mr-arch/Codex_Skills 저장소의 스킬 6개를 내 Codex에 설치해줘.
저장소를 내려받고 SKILL.md가 있는 각 폴더 전체를 사용자 스킬 경로 ~/.agents/skills에 복사해줘.
이미 같은 이름이 있으면 변경 내용을 확인하고 알려줘.
설치가 끝나면 스킬 목록과 호출 예시를 보여줘.
```

하나만 필요하면 이렇게 요청합니다.

```text
$skill-installer https://github.com/9mr-arch/Codex_Skills/tree/main/cinematic-video-prompts 에 있는 스킬을 설치해줘.
```

설치 후 새 대화에서 `$cinematic-video-prompts`처럼 이름을 지정해 사용합니다. 목록에 나타나지 않으면 Codex를 다시 시작하세요.

```text
$cinematic-video-prompts 첨부한 스타일프레임의 구도를 살려 15초 광고 영상 프롬프트를 작성해줘.
```

폴더 단위 설치와 `$skill-installer` 사용은 [공식 스킬 안내](https://learn.chatgpt.com/docs/build-skills)를 참고했습니다. 스킬은 작업 지침이며, 이미지 생성 도구나 3D 모델 가중치가 함께 설치되는 패키지는 아닙니다.

각 하위 폴더는 독립적으로 설치할 수 있는 Codex 스킬입니다. 원하는 폴더를 그대로 복사하면 됩니다.

## 포함된 스킬

- `beauty-character-sheet` — 광고용 실사 모델 캐릭터 시트
- `cinematic-video-prompts` — TVCF·드라마·패션 등 실사 영상 프롬프트 설계
- `seedance-reference-video` — 프리비즈·실사 레퍼런스 영상을 Seedance 2.0 프롬프트로 변환
- `trellis2-image-to-glb` — 한 장 또는 여러 장의 이미지에서 텍스처 포함 GLB 제작
- `gaussian-splatting` — 이미지·사진·영상에서 Gaussian Splatting 및 Blender용 PLY 제작
- `reference-to-style-prompts` — 스타일 레퍼런스에서 6컷 이미지 프롬프트와 영상 MOOD 지침 추출

## Windows에서 설치

PowerShell에서 이 폴더로 이동한 뒤 전체 스킬을 설치합니다.

```powershell
.\install-skills.ps1
```

특정 스킬만 설치할 수도 있습니다.

```powershell
.\install-skills.ps1 -Names seedance-reference-video,reference-to-style-prompts
```

이미 같은 이름의 스킬이 있으면 기본적으로 중단합니다. 의도적으로 업데이트하려면 `-Force`를 붙입니다.

```powershell
.\install-skills.ps1 -Names seedance-reference-video -Force
```

기본 설치 대상은 사용자 홈의 `.agents\skills`입니다. 기존 환경에서 다른 경로를 사용한다면 `-DestinationRoot '원하는 경로'`로 지정할 수 있습니다. 설치 후 목록에 보이지 않으면 Codex를 다시 시작합니다.

## 수동 설치

원하는 스킬 폴더 전체를 아래 위치로 복사합니다.

```text
Windows: %USERPROFILE%\.agents\skills\<skill-name>
macOS/Linux: ~/.agents/skills/<skill-name>
```

`SKILL.md`만 따로 떼지 말고 `agents/`, `references/`, `scripts/`가 있는 경우 함께 복사해야 합니다.

## 실행 환경 주의사항

프롬프트 작성형 스킬은 별도 설치 없이 사용할 수 있습니다. `trellis2-image-to-glb`와 `gaussian-splatting`은 GPU, Python, 모델 가중치 및 외부 오픈소스 도구가 필요할 수 있으며, 스킬이 현재 환경을 조사한 뒤 호환 가능한 실행 경로를 선택하거나 의존성 파일들을 설치합니다. `seedance-reference-video`의 로컬 영상 분석기는 Python과 OpenCV·NumPy가 있으면 대표 프레임과 콘택트시트를 자동 추출합니다.
