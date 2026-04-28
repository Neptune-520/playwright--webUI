import json

import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import GlobalConfig


def get_marketplace_api_base():
    try:
        config = GlobalConfig.get_config()
        return config.marketplace_api_url
    except:
        return getattr(settings, 'MARKETPLACE_API_BASE', 'http://127.0.0.1:8000')


def _marketplace_get(path, params=None):
    try:
        api_base = get_marketplace_api_base()
        url = f'{api_base}{path}'
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json(), resp.status_code
    except requests.exceptions.ConnectionError:
        return {'error': '无法连接到自动化管理平台'}, 503
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


def _marketplace_post(path, files=None, params=None):
    try:
        api_base = get_marketplace_api_base()
        url = f'{api_base}{path}'
        resp = requests.post(url, files=files, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json(), resp.status_code
    except requests.exceptions.ConnectionError:
        return {'error': '无法连接到自动化管理平台'}, 503
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


def _get_file_metadata(data):
    if isinstance(data, dict):
        return data.get('name', ''), data.get('description', '') or '无描述'
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return data[0].get('name', ''), data[0].get('description', '') or '无描述'
    return '', '无描述'


def _enrich_items_with_metadata(items, path):
    params = {}
    if path:
        params['path'] = path
    for item in items:
        if not item.get('is_folder') and item.get('name', '').endswith('.json'):
            try:
                preview_data, _ = _marketplace_get(f'/api/items/{item["name"]}/preview', params)
                if isinstance(preview_data, dict):
                    item['_name'] = preview_data.get('name', '')
                    item['_description'] = preview_data.get('description', '') or '无描述'
                else:
                    item['_name'], item['_description'] = _get_file_metadata(preview_data)
            except:
                item['_name'] = ''
                item['_description'] = '无描述'
        if path:
            item['_path'] = path


@api_view(['GET'])
@permission_classes([AllowAny])
def marketplace_list_items(request):
    path = request.query_params.get('path', '')
    params = {}
    if path:
        params['path'] = path
    data, status_code = _marketplace_get('/api/items', params)
    if status_code == 200 and isinstance(data, list):
        _enrich_items_with_metadata(data, path)
    return Response(data, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def marketplace_search_items(request):
    keyword = request.query_params.get('keyword', '')
    if not keyword:
        return Response([])

    data, status_code = _marketplace_get('/api/search', {'keyword': keyword})
    if status_code != 200:
        return Response(data, status=status_code)

    results = []
    for item in data:
        if isinstance(item, dict) and not item.get('is_folder'):
            item['_name'] = ''
            item['_description'] = '无描述'
            item['_path'] = item.get('path', '')
            results.append(item)

    return Response(results, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def marketplace_create_folder(request):
    name = request.data.get('name', '')
    path = request.data.get('path', '')
    if not name:
        return Response({'error': '文件夹名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    params = {'name': name}
    if path:
        params['path'] = path

    data, status_code = _marketplace_post('/api/folder', params=params)
    return Response(data, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def marketplace_download_file(request):
    name = request.query_params.get('name', '')
    path = request.query_params.get('path', '')
    if not name:
        return Response({'error': '文件名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    params = {}
    if path:
        params['path'] = path
    data, status_code = _marketplace_get(f'/api/items/{name}/preview', params)
    return Response(data, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def marketplace_preview_file(request):
    name = request.query_params.get('name', '')
    path = request.query_params.get('path', '')
    if not name:
        return Response({'error': '文件名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    params = {}
    if path:
        params['path'] = path
    data, status_code = _marketplace_get(f'/api/items/{name}/preview', params)
    return Response(data, status=status_code)


@api_view(['POST'])
@permission_classes([AllowAny])
def marketplace_upload_file(request):
    name = request.data.get('filename', '')
    path = request.data.get('path', '')
    file_content = request.data.get('content', '')
    if not name or not file_content:
        return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)

    params = {}
    if path:
        params['path'] = path
    files = {
        'file': (name, json.dumps(file_content, ensure_ascii=False, indent=2).encode('utf-8'), 'application/json')
    }
    data, status_code = _marketplace_post('/api/upload', files=files, params=params)
    return Response(data, status=status_code)
