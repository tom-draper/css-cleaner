import sys
import os
import re


def collect_files(extensions):
    # Get list of all files
    all_files = []
    for root, dirs, files in os.walk('./'):
        for f in files:
            all_files.append(os.path.join(root, f))

    # Remove invalid files
    for i in range(len(all_files)-1, -1, -1):
        ext = all_files[i].split('.')[-1]
        if ext not in extensions:
            all_files.pop(i)

    return all_files


def extract_css_styles(css):
    styles = set()
    for style_tag in re.findall(r'\n([^:\n@%]*)\{', css):
        styles = styles.union(set(style_tag.strip().split(' ')))
    print(len(styles), 'styles found')
    return styles


def filter_used_classes(styles, html):
    for classes in re.findall(r'class="(.*)"', html):
        for _class in classes.split(' '):
            try:
                styles.remove('.' + _class)
            except:
                pass


def filter_used_ids(styles, html):
    for ids in re.findall(r'id="(.*)"', html):
        for _id in ids.split(' '):
            try:
                styles.remove('#' + _id)
            except:
                pass


def filter_used_tags(styles, html):
    to_remove = set()
    for style in styles:
        if '.' not in style and '#' not in style and '<' + style in html:
            to_remove.add(style)
    styles = styles - to_remove


def filter_html_used(styles):
    html_files = collect_files({'html', 'svelte', 'vue'})
    for file_path in html_files:
        with open(file_path, 'r') as f:
            html = f.read()
            filter_used_classes(styles, html)
            filter_used_ids(styles, html)
            filter_used_tags(styles, html)


def filter_js_used(styles):
    js_files = collect_files({'js', 'mjs', 'svelte', 'vue', 'html'})
    to_remove = set()
    for file_path in js_files:
        with open(file_path, 'r') as f:
            js = f.read()
            # Any mention of style within js -> assume style used and added using js
            for style in styles:
                if style.replace('.', '').replace('#', '') in js:
                    to_remove.add(style)
    styles = styles - to_remove
    print('Ignoring styles mentioned in JavaScript', to_remove)


def remove_styles(css, styles):
    for style in styles:
        css = re.sub(r'\n\s*' + style.replace('*', '\*') + r'\s*{[^}]*}', '', css)
        css = re.sub(style.replace('*', '\*') + r',\s*\n', '', css)
        print(f'Removed {style}')
        
    return css


def remove_unused_styles(css):
    styles = extract_css_styles(css)

    # Search through all classes and ids used across all HTML and remove used
    filter_html_used(styles)
    # CSS classes may be added using javascript
    filter_js_used(styles)

    # Styles remaining in set are not used any html or js file
    # EXCEPTION: Inserting a class using js without explicitly stating the class
    #            name within the js file
    print('To remove', len(styles), 'styles:', styles)
    css = remove_styles(css, styles)
    
    return css


def remove_duplicate_styles(css):
    pass


def merge_duplicate_style_tags(css):
    pass


def run(path):
    with open(path, 'r') as f:
        css = f.read()

    css = remove_unused_styles(css)
    # Remove any overridden styles for each class
    css = remove_duplicate_styles(css)
    # Merge duplicate style tags
    css = merge_duplicate_style_tags(css)


def get_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return None


if __name__ == '__main__':
    path = get_path()
    run(path)
