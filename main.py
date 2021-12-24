import requests
import plotly.graph_objects as go
import networkx as nx
import time
import matplotlib.pyplot as plt
from PersonalData import access_token

api_version = '5.131'
my_id = '167196653'
read_id = input("Type interested vk id or write \"0\" to use default: ")
if read_id != '0':
    my_id = read_id
    print("my_id changed", my_id)
friend_num = int(input("Type how many friends you want to show or write \"0\" show all: "))


params_for_users_get = {'user_ids': my_id,
                        'access_token': access_token,
                        'v': api_version}

myFirstAndLastName = requests.get('https://api.vk.com/method/users.get', params=params_for_users_get)
#print(myFirstAndLastName.text)

params_for_friends_get = {'user_id': my_id,
                          'order': 'hints',
                          'fields': 'sex',
                          'access_token': access_token,
                          'v': api_version}

r = requests.get('https://api.vk.com/method/friends.get', params=params_for_friends_get)
if 'error' in r.json() and r.json()['error']['error_code'] == 30:
    print('This is private profile, sorry')
    exit()
print(r.text)
AllMyFriends = r.json()['response']['items']
#print(AllMyFriends[0]['id'])
#print(AllMyFriends[0]['is_closed'])
#print(AllMyFriends)
AllMyFriendsWithoutClosed = [i for i in AllMyFriends if 'is_closed' in i and i['is_closed'] == False]
if friend_num == 0:
    friend_num = len(AllMyFriendsWithoutClosed)

G = nx.Graph()


def GetFriendListById(friend_id):
    while True:
        params_for_another_friends_get = {'user_id': friend_id,
                                          'order': 'random',
                                          'access_token': access_token,
                                          'v': api_version}
        res = requests.get('https://api.vk.com/method/friends.get', params=params_for_another_friends_get)
        print(res.text)
        res_json = res.json();
        if 'error' in res_json:
            if res_json['error']['error_code'] == 6:
                time.sleep(0.8)
                continue
            if res_json['error']['error_code'] == 30:
                return [], False
            return [], False
        if 'response' in res_json:
            return res_json['response']['items'], True
        return [], False


MyFriends = AllMyFriendsWithoutClosed[:friend_num-1]
#MyFriends.append(myFirstAndLastName.json()['response'][0])
MyFriendsSet = set([i['id'] for i in MyFriends])
MyFriendsDict = dict([(i['id'], i) for i in MyFriends])
MyFriendsDict[int(my_id)] = myFirstAndLastName.json()['response'][0]
#print(MyFriends)
#print(G.nodes())
for friend_id in MyFriends:
    friendFriendList, Flag = GetFriendListById(friend_id['id'])
    if not Flag:
        continue
    G.add_edge(friend_id['id'], int(my_id))
    for friendFriend_id in friendFriendList:
        if friendFriend_id in MyFriendsSet:
            G.add_edge(friend_id['id'], friendFriend_id)

G_nodes_list = list(G.nodes)
#print(G_nodes_list)

pos = nx.spring_layout(G)
#print(pos)

nx.draw_networkx_nodes(G, pos, node_size=50)
nx.draw_networkx_edges(G, pos, edge_color='b')
plt.show()

edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos.get(edge[0])  # G.nodes[edge[0]]['pos']
    x1, y1 = pos.get(edge[1])  # G.nodes[edge[1]]['pos']
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
for node in G.nodes():
    # print(node)
    x, y = pos.get(node)  # G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Edges',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

node_adjacencies = []
node_text = []
#print(MyFriendsDict)
# print(G_nodes_list[1])
# print(MyFriendsDict[G_nodes_list[1]]['first_name'])
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append(MyFriendsDict[G_nodes_list[node]]['first_name'] + ' ' + MyFriendsDict[G_nodes_list[node]]['last_name'] + ' ' + str(len(adjacencies[1])) + ' edges')
    #  print(node)

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='<br>Social graph to ' + myFirstAndLastName.json()['response'][0]['first_name'] + ' ' + myFirstAndLastName.json()['response'][0]['last_name'],
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[dict(
                        text="Python code: <a href='https://github.com/Akuva2001/SocialGraph'> https://github.com/Akuva2001/SocialGraph</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.005)],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
fig.show()
