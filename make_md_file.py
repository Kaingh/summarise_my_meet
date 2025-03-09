from snakemd import Document, MDList, Inline

def create_md_file_object(contents):
    readme = Document()
    mapper = {
    'l2_summary'        : 'Short Summary',
    'detailed_output'   : 'Detailed Summary',
    'key_insights'      : 'Key Insights',
    'quotes'            : 'Quotes',
    'action_points'     : 'Action Points',
    'kpi_matrices'      : 'Key Metrics'
    }
    for key,value in contents.items():
        readme.add_heading(mapper[key])
        if len(value) and isinstance(value, list):
            content = []
            for line in value:
                content.append(Inline(line))
            readme.add_block(MDList(content))
            readme.add_horizontal_rule()
        elif len(value) and isinstance(value,str):
            readme.add_paragraph(value)
            readme.add_horizontal_rule()
        else:
            readme.add_paragraph('')
            readme.add_horizontal_rule()
    return str(readme)