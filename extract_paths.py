import pathlib
import sys
import yaml


def get_dict_without_paths_except(dict_value: dict, paths_to_abandon):
    all_paths = dict_value.get('paths')
    paths_to_abandon_dict = {}
    for path in paths_to_abandon:
        paths_to_abandon_dict[path] = all_paths.get(path)
    dict_value['paths'] = paths_to_abandon_dict
    return dict_value


def get_schemas_refs(dict_value: dict):
    result = {}
    for key, schema in dict_value.items():
        result[key] = get_refs_from_item(schema)
    return result


def get_refs_from_item(item):
    refs = {}

    def wide_search(node):
        if isinstance(node, str) and node.startswith('#/components/'):
            path_items = node.rsplit('/')
            if path_items[2] in refs:
                refs[path_items[2]].add(path_items[3])
            else:
                refs.update({path_items[2]: {path_items[3]}})
        elif isinstance(node, dict):
            for _, v in node.items():
                wide_search(v)
        elif isinstance(node, list):
            for item in node:
                wide_search(item)

    wide_search(item)
    return refs


def remove_useless_schemas(spec):
    obj_refs_from_paths = get_refs_from_item(spec.get('paths'))
    all_objects = {}
    all_refs = {}
    for name, block in spec.get('components', {}).items():
        all_objects[name] = block
        all_refs[name] = get_schemas_refs(block)

    used_objects = {}

    def update_used_objects(folder, obj):
        used_objects[obj] = folder
        for f, refs in all_refs.get(folder).get(obj).items():
            for ref in refs:
                if ref not in used_objects:
                    update_used_objects(f, ref)

    for folder, objects in obj_refs_from_paths.items():
        for obj in objects:
            update_used_objects(folder, obj)

    used_objects_with_content = {}
    for obj, folder in used_objects.items():
        if folder in used_objects_with_content:
            used_objects_with_content[folder].update({obj: all_objects[folder][obj]})
        else:
            used_objects_with_content.update({folder: {obj: all_objects[folder][obj]}})
    spec['components'].update(used_objects_with_content)


if __name__ == '__main__':
    in_path = pathlib.Path(sys.argv[1])
    out_path = pathlib.Path(sys.argv[2])
    paths_to_abandon = [x.replace(' ', '') for x in sys.argv[3:]]

    with in_path.open('r') as file:
        spec = yaml.safe_load(file.read())

    result_spec = get_dict_without_paths_except(spec, paths_to_abandon)
    remove_useless_schemas(result_spec)

    out_path.write_text(
        yaml.dump(result_spec, allow_unicode=True)
    )

