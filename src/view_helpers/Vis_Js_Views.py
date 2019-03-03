from utils.Dev import Dev
from utils.Misc import Misc
from utils.aws.Lambdas import load_dependencies
from view_helpers.Node_Format import Node_Format


class Vis_Js_Views:

    @staticmethod
    def default(team_id=None, channel=None, params=None, no_render=False):

        load_dependencies(['syncer', 'requests']) ; from view_helpers.Vis_Js import Vis_Js

        graph_name = params.pop(0)
        vis_js = Vis_Js()
        graph_data = vis_js.get_graph_data(graph_name)
        nodes = []
        edges = []
        vis_js.load_page(False)
        if graph_data:
            for key, issue in graph_data.get('nodes').items():
                nodes.append({'id': key, 'label': key})
                # Dev.pprint(issue)

            for edge in graph_data.get('edges'):
                from_node = edge[0]
                link_type = edge[1]
                to_node = edge[2]
                edges.append({'from': from_node, 'to': to_node, 'label': link_type})

            if no_render is False:
                vis_js.create_graph(nodes, edges)

        if no_render is True:
            return (nodes, edges, graph_data,vis_js)

        return vis_js.send_screenshot_to_slack(team_id, channel)

    @staticmethod
    def no_labels(team_id=None, channel=None, params=None):

        (nodes, edges, graph_data,vis_js) = Vis_Js_Views.default(params=params, no_render=True)

        for node in nodes:
            del node['label']

        for edge in edges:
            del edge['label']

        return vis_js.create_graph_and_send_screenshot_to_slack(nodes,edges, None, team_id, channel)

    @staticmethod
    def node_label(team_id=None, channel=None, params=None):

        if len(params) < 2:
            return "':red_circle: Hi, for the `node_label` view, you need to provide the label field name. Try: `Key`, `Summary`, `Rating`, `Status`"

        #graph_name = params[0]
        label_key  = ' '.join(params[1:])
        #label_key = params[1]

        (nodes, edges, graph_data,vis_js) = Vis_Js_Views.default(params=params, no_render=True)

        issues = graph_data.get('nodes')
        for node in nodes:
            issue = issues.get(node['label'])
            if issue:
                value = str(issue.get(label_key))
                node['label'] = Misc.word_wrap(value,40)

        for edge in edges:
            del edge['label']

        options = { 'nodes': {'shape' : 'box' },
                    'edges': {'arrows': 'to'  }}
        options = None
        return vis_js.create_graph_and_send_screenshot_to_slack(nodes,edges, options, team_id, channel)

    # Issues layouts

    @staticmethod
    def by_status(team_id=None, channel=None, params=None):
        (nodes, edges, graph_data, vis_js) = Vis_Js_Views.default(params=params, no_render=True)
        issues = graph_data.get('nodes')
        options ={}
        for node in nodes:
            issue = issues.get(node.get('id'))
            (
                    Node_Format .rating_color(node, issue)
                                .size_by_r123(node, issue)
                                .set_Label   (node, issue, 'Summary')
                                .only_highs  (node, issue)
                                #.add_Key_to_Label(node)
            )

        for edge in edges:
            edge['label'] = ''

        return (    vis_js.load_page(True)
                          .create_graph(nodes, edges, options)
                          .browser_width(3000)
                          .send_screenshot_to_slack(team_id, channel) )

    @staticmethod
    def r0_r1_r2(team_id=None, channel=None, params=None):

        options = {
            'nodes': { 'shape' : 'box'},
            'edges': { 'arrows': 'to' },
            'physics': {
                'barnesHut': {
                    'avoidOverlap': 0.1
                },
            }}

        (nodes, edges, graph_data, vis_js) = Vis_Js_Views.default(params=params, no_render=True)

        def format_node(node):
            issue = graph_data.get('nodes').get(node.get('id'))
            if issue:
                node['label'] = Misc.word_wrap(issue.get('Summary'),20)
                node['label'] = issue.get('Rating')
                labels = issue.get('Labels')
                if 'R0' in labels:
                    #node['label'] = issue.get('Summary')
                    node['color'] = '#FF0000'
                    node['font' ] = {'color' : 'white', 'size': 25 }
                    node['mass' ] = 2
                    return node

                if 'R1' in labels:
                    node['color'] = '#FF6666'
                    node['font'] = {'size': 20}
                    node['mass'] = 3
                    return node

                if 'R2' in labels:
                    node['color'] = '#FFAAAA'
                    node['font'] = {'size': 15}
                    #node['mass'] = 1
                    return node

                #if 'R3' in labels:
                #    node['color'] = '#FFDDDD'
                return node
                #Dev.pprint(issue)

        fixed_nodes = []
        for node in nodes:
            fixed_node = format_node(node)
            if fixed_node:
                fixed_nodes.append(fixed_node)

        for edge in edges:
            edge['label'] =''

        #edges = []
        vis_js.load_page(True)
        vis_js.create_graph(fixed_nodes, edges, options)
        vis_js.browser().sync__browser_width(400)
        return vis_js.send_screenshot_to_slack(team_id, channel)
        #return vis_js.create_graph_and_send_screenshot_to_slack(fixed_nodes, edges, options, team_id, channel)
