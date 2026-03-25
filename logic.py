import json


def parse_instagram_json(file_path):
    """
    Instagram JSON 내보내기 파일을 파싱하여 유저명 집합을 반환합니다.
    알려진 모든 Instagram JSON 포맷을 지원합니다.
    """
    usernames = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        data = json.loads(raw)
    except UnicodeDecodeError:
        # utf-8 실패 시 latin-1 시도
        with open(file_path, 'r', encoding='latin-1') as f:
            raw = f.read()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 형식 오류: {e}")
    except FileNotFoundError:
        raise ValueError(f"파일을 찾을 수 없습니다: {file_path}")

    # ── 포맷 정규화: dict → list ──────────────────────────────
    # 형식 A) {"relationships_following": [...]}
    # 형식 B) {"relationships_followers": [...]}
    # 형식 C) {"data": {"relationships_following": [...]}}  (드문 경우)
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        # 모든 값을 순회하며 리스트를 찾음
        for val in data.values():
            if isinstance(val, list):
                items = val
                break
            # 한 단계 더 들어가기 (중첩 dict)
            if isinstance(val, dict):
                for inner_val in val.values():
                    if isinstance(inner_val, list):
                        items = inner_val
                        break
                if items:
                    break

    # ── 유저명 추출 ───────────────────────────────────────────
    for item in items:
        if not isinstance(item, dict):
            if isinstance(item, str) and item.strip():
                usernames.add(item.strip())
            continue

        found = False

        # 형식 1: {"string_list_data": [{"value": "username", ...}]}
        # string_list_data가 있어도 비어있을 수 있으므로 found 여부를 확인 후 계속 진행
        if 'string_list_data' in item:
            sld = item['string_list_data']
            if isinstance(sld, list) and sld:
                v = sld[0].get('value', '').strip()
                if v:
                    usernames.add(v)
                    found = True

        if found:
            continue

        # 형식 2: {"value": "username"}
        if 'value' in item:
            v = str(item['value']).strip()
            if v:
                usernames.add(v)
                continue

        # 형식 3: {"title": "username"}
        #  → following.json에서 string_list_data가 비어있을 때 여기서 추출
        if 'title' in item:
            v = str(item['title']).strip()
            if v:
                usernames.add(v)
                continue

        # 형식 4: {"username": "..."}
        if 'username' in item:
            v = str(item['username']).strip()
            if v:
                usernames.add(v)
                continue

        # 형식 5: {"user": {"username": "..."}}
        if 'user' in item and isinstance(item['user'], dict):
            v = str(item['user'].get('username', '')).strip()
            if v:
                usernames.add(v)
                continue

    return usernames


def get_unfollowers_data(followers_path, following_path):
    """
    팔로워와 팔로잉 파일을 비교하여 결과를 반환합니다.
    """
    followers = parse_instagram_json(followers_path)
    following = parse_instagram_json(following_path)

    if not followers and not following:
        raise ValueError(
            "두 파일 모두 유저 정보를 파싱하지 못했습니다.\n"
            "올바른 Instagram 데이터 내보내기 JSON 파일인지 확인하세요.\n"
            "diagnose.py를 실행하면 상세 구조를 확인할 수 있습니다."
        )

    # 소문자 정규화 비교 (대소문자 불일치 방지)
    followers_lower = {u.lower(): u for u in followers}
    following_lower = {u.lower(): u for u in following}

    f_set = set(followers_lower.keys())
    g_set = set(following_lower.keys())

    unfollowers_keys = g_set - f_set
    fans_keys = f_set - g_set
    mutuals_keys = f_set & g_set

    # 원본 대소문자 복원
    unfollowers = sorted([following_lower[k] for k in unfollowers_keys])
    fans = sorted([followers_lower[k] for k in fans_keys])
    mutuals = sorted([followers_lower[k] for k in mutuals_keys])

    return {
        "unfollowers": unfollowers,
        "fans": fans,
        "mutuals": mutuals,
        "following_count": len(following),
        "followers_count": len(followers),
    }
