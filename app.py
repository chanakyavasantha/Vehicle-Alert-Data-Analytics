from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import pandas as pd
import plotly.express as px
import io
import base64
import matplotlib.pyplot as plt
from plotly import io as pio


df = pd.read_csv('static/iraste_nxt_cas.csv')
df1 = pd.read_csv('static/iraste_nxt_casdms.csv')
df = pd.concat([df, df1], axis = 0)
df = df.drop_duplicates()
df = df.dropna()
df = df.sample(frac=0.01, random_state=42)




# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return

    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)


@on('#intro')
async def page_intro(q: Q):
    q.page['sidebar'].value = '#intro'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='1000px'), title='Spatial Analysis',
        image='https://i.ibb.co/fYDMvzw/Screenshot-2024-03-17-at-12-05-30-AM.png',
        content='''
Data Analysis of Traffic in Busy Roads connecting south indian cities.
        '''
    ))

@on('#data-frame-analysis')
async def page_df(q: Q):
    q.page['sidebar'].value = '#data-frame-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q)
    table_rows = []
    df['Speed'] = df['Speed'].astype(str)
    for index, row in df.iterrows():
        if index == 10000:
            break
        table_rows.append(ui.table_row(
            name=row['Date'],
            cells=[row['Date'], row['Alert'],row['Speed']]  # Adjust these indices based on your CSV columns
        ))
    add_card(q, 'table', ui.form_card(box='vertical', items=[ui.table(
        name='table',
        downloadable=True,
        resettable=True,
        groupable=True,
        columns=[
            ui.table_column(name='Date', label='Date', searchable=True,min_width='500'),
            ui.table_column(name='Alert', label='Alert', filterable=True, min_width='500',cell_type=ui.tag_table_cell_type(name='tags', tags=[
                    ui.tag(label='RUNNING', color='#D2E3F8'),
                    ui.tag(label='DONE', color='$red'),
                    ui.tag(label='SUCCESS', color='$mint'),
                    ]
                )),
            ui.table_column(name='Speed', label='Speed', searchable=True,min_width='500'),
        ],
        events = ['click'],
        rows=table_rows)
    ]))

@on('table')
async def handle_table_click(q: Q):
    table_rows = []
    for index, row in df.iterrows():
        table_rows.append(ui.table_row(
            name=row['title'],
            cells=[row['title'], row['News source'],]  # Adjust these indices based on your CSV columns
        ))
    print(q.args.table)
    if q.args.table:
        q.client.selected_actor = q.args.table[0]
        q.args['#'] = 'data-frame-analysis'
        await page_df(q)

@on('#alert-frequency-analysis')
async def pageca(q: Q):
    print('Handling page4')

    q.page['sidebar'].value = '#alert-frequency-analysis'
    clear_cards(q)


    # Assuming df is your DataFrame containing the dataset

    # Convert 'Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Extract day of the week and hour of the day from the 'Date' column
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['HourOfDay'] = df['Date'].dt.hour

    # Alert Frequency Analysis by Day of Week
    fig1 = px.histogram(df, x='DayOfWeek', color='Alert', title='Alert Frequency by Day of Week')
    fig1.update_layout(xaxis={'categoryorder':'total descending'},width = 1300)

    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig1, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'bar1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='650px', width='1300px')]))

    fig3 = px.scatter(df, x='Speed', color='Alert', title='Alert Frequency Comparison Across Different Vehicles')
    fig3.update_layout(xaxis_title='Speed', yaxis_title='Alert Frequency', width = 1300)
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig3, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'bar2', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html, height='650px', width='1300px')]))
   

@on('#industry-sector-sentiment-analysis')
async def page_ind(q: Q):
    q.page['sidebar'].value = '#industry-sector-sentiment-analysis'
    clear_cards(q)  # When routting, drop all the cards except of the main ones (header, sidebar, meta).
    '''
    add_card( q, 'dataframe', ui.form_card(box='zone2', items=[
        # modify heading here (content)
        ui.text_xl(content='Data Frame Head'),
        ui.table(
            name='table',
            columns=[ui.table_column(name=i, label=i, min_width='200',cell_type=ui.markdown_table_cell_type(target='_blank')) for i in df.columns],
            height='400px',
            rows=[ui.table_row(name=f'row{i}', cells=list(str(i) for i in df.values[i])) for i in range(100)],
        )
    ]))
    '''
    # Identify the top 10 industry sectors with positive sentiment
    # Assuming you have a 'Sentiment' column in your DataFrame
    positive_rows = df[df['Sentiment'].str.lower().str.contains('positive')]
    

    # Extract the top 10 industry sectors with positive sentiment
    
    # Assuming you already have 'positive_rows' DataFrame
    # Extract the top 10 industry sectors with positive sentiment
    positive_industries = positive_rows['Industry sector'].value_counts().head(10)
    positive_industries = positive_industries[1:]

    # Create a pie chart using plotly express
    fig = px.pie(positive_industries, 
             names=positive_industries.index, 
             values=positive_industries.values, 
             title='Top 10 Industry Sectors with Positive Sentiment')
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'piechart1', ui.frame_card(box='horizontal', title='', content=html))
    # Identify the top 10 industry sectors with negative sentiment
    # Assuming you have a 'Sentiment' column in your DataFrame
    negative_rows = df[df['Sentiment'].str.lower().str.contains('negative')]
    # Extract the top 10 industry sectors with negative sentiment
    negative_industries = negative_rows['Industry sector'].value_counts().head(10)
    add_card(q, 'dataframe3', ui.form_card(box='horizontal', items=[
        ui.text_xl(content='Top 10 Industry Sectors with Most Negative Sentiment'),
        ui.table(
            name='negative_table',
            columns=[
                ui.table_column(name='Industry Sector', label='Industry Sector', min_width='200'),
                ui.table_column(name='Count', label='Negative Sentimental NewsCount', min_width='200')
            ],
            rows=[ui.table_row(name = f'count{count}',cells=[sector , str(count)]) for sector, count in negative_industries.items() if sector != '0'],
            height='400px',
        )
    ]))
    positive_news_source = positive_rows['News source'].value_counts().head(13)
    del positive_news_source['0']
    del positive_news_source['Not mentioned']
    del positive_news_source['Not specified.']
    fig = px.pie(positive_news_source,
                 names = positive_news_source.index,
                 values = positive_news_source.values,
                 title = 'Top 10 Positive News Sources')
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'piechart2', ui.frame_card(box='zone1', title='', content=html))
    

    negative_news_source = negative_rows['News source'].value_counts().head(10)
    add_card(q, 'datafram2', ui.form_card(box='zone1', items=[
        ui.text_xl(content='Top 10 Negative News Sources'),
        ui.table(
            name='negative_table_News_source',
            columns=[
                ui.table_column(name='Industry Sector', label='Industry Sector', min_width='200'),
                ui.table_column(name='Count', label='Negative Sentimental NewsCount', min_width='200')
            ],
            rows=[ui.table_row(name = f'count{count}',cells=[sector , str(count)]) for sector, count in negative_news_source.items() if sector != '0'],
            height='400px'
        )
    ]))
    


@on('#temporal-analysis')
async def page_temporal(q: Q):
    q.page['sidebar'].value = '#temporal-analysis'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    
    # Create a histogram using Plotly for temporal distribution
    fig_temporal = px.histogram(df, x='date', nbins=30, labels={'date': 'Date', 'count': 'Number of Articles'})
    fig_temporal.update_layout(title='Temporal Distribution of Articles', xaxis_title='Date', yaxis_title='Number of Articles')
    config_temporal = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html_temporal = pio.to_html(fig_temporal, validate=False, include_plotlyjs='cdn', config=config_temporal)
    add_card(q, 'temporal1', ui.form_card(box=ui.box('horizontal', width='750px'), title='', items=[
        ui.frame(content=html_temporal, height='650px', width='650px')]))

    # Create a grouped bar chart for industry representation
    fig_industry = px.histogram(df, x='date', color='Industry sector', nbins=30,
                                 labels={'date': 'Date', 'count': 'Number of Articles', 'Industry sector': 'Industry'})
    fig_industry.update_layout(title='Industry Representation Over Time', xaxis_title='Date', yaxis_title='Number of Articles')
    config_industry = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html_industry = pio.to_html(fig_industry, validate=False, include_plotlyjs='cdn', config=config_industry)
    add_card(q, 'industry1', ui.form_card(box=ui.box('vertical', width='1500px'), title='', items=[
        ui.frame(content=html_industry, height='650px', width='1500px')]))

    


    

    






@on('#ind-sub-analysis')
@on('page4_reset')
async def page4(q: Q):
    q.page['sidebar'].value = '#ind-sub-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # Now df_expanded has each industry on a separate row

    

    # Plot Industry Distribution
    fig_industry = px.bar(industry_distribution, x='Industry', y='Count', title='Distribution of News Across Industries')
    fig_industry.update_layout(xaxis_title='Industry', yaxis_title='Number of Articles')
    fig_industry.update_traces(width=2)
    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig_industry, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'ind1', ui.form_card(box=ui.box('horizontal',width='1500px'), title='', items=[
        ui.frame(content=html, height='1000px',width='1500px')]))

@on('#target-audience-analysis')
async def page_target_aud(q: Q):
    q.page['sidebar'].value = '#target-audience-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    


    # Plot Target Audience Distribution
    fig_target_audience = px.bar(target_audience_distribution, x='Target Audience', y='Count', title='Target Audience Analysis')

    # Increase bar width if needed
    fig_target_audience.update_layout(yaxis_range=[0, 100])
    fig_target_audience.update_traces(width=3)


    config = {
        'scrollZoom': False,
        'showLink': False,
        'displayModeBar': False
    }
    html = pio.to_html(fig_target_audience, validate=False, include_plotlyjs='cdn', config=config)
    add_card(q, 'aud1', ui.form_card(box=ui.box('horizontal',width='1500px'), title='', items=[
        ui.frame(content=html, height='1000px',width='1500px')]))

    

@on('#competitor-analysis')
async def page_comp(q: Q):
    q.page['sidebar'].value = '#competitor-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q)

@on('#salary-analysis')
async def page_salary(q: Q):
    q.page['sidebar'].value = '#salary-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q)

@on('#cross-industry-analysis')
async def page_cross(q: Q):
    q.page['sidebar'].value = '#cross-industry-analysis'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q)

def plot_categorical_graph(df, selected_column):
    # Assuming data is present in a column named 'data'
    fig = px.histogram(df, x=selected_column, title=f'Distribution of {selected_column}')
    return fig




    




@on()
async def page4_step2(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step3', label='Next', primary=True),
        ])
    ]


@on()
async def page4_step3(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_reset', label='Finish', primary=True),
        ])
    ]


async def init(q: Q) -> None:
    q.page['meta'] = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
            ui.zone('sidebar', size='300px'),
            ui.zone('body', zones=[
                ui.zone('header'),
                ui.zone('content', zones=[
                    # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                    ui.zone('horizontal', direction=ui.ZoneDirection.ROW,),
                    ui.zone('zone2',direction=ui.ZoneDirection.ROW ),
                    ui.zone('vertical'),
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center'),
                    ui.zone(name='zone1', direction=ui.ZoneDirection.ROW),
                    ui.zone(name='zone3',direction=ui.ZoneDirection.COLUMN)
                ]),
            ]),
        ])
    ])])
    q.page['sidebar'] = ui.nav_card(
        box='sidebar', color='primary', title = 'Advanced Driver Assistance System', subtitle="",
        value=f'#{q.args["#"]}' if q.args['#'] else '#intro',
        image='', items=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#intro', label='Spatial Analysis'),
                ui.nav_item(name='#data-frame-analysis', label='Data Frame Analysis'),
                ui.nav_item(name='#alert-frequency-analysis', label='Alert Freuency Analysis'),
                ui.nav_item(name='#speed-analysis', label='Speed Analysis'),
                ui.nav_item(name='#correlation-analysis', label='Correlation Analysis'),
                ui.nav_item(name='#driver-behaviour-analysis', label='Driver Behaviour Analysis'),
                ui.nav_item(name='#comparitive-analysis',label='Comparitive Analysis'),
                ui.nav_item(name='#safety-impact-analysis',label='Safety Impact Analysis'),
                
            ]),
        ],
    )
    q.page['header'] = ui.header_card(
        box='header', title='', subtitle='',
    )

    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page_intro(q)


@app('/')
async def serve(q: Q):
    # Run only once per client connection.
    if not q.client.initialized:
        q.client.cards = set()
        await init(q)
        q.client.initialized = True

    # Handle routing.
    await run_on(q)
    await q.page.save()
