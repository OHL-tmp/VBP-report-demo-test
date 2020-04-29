

# generate selected domain button

'''def generate_card_domain_button(color):
    if color == "primary":
        return False
    return True

for i in range(domain_ct):
    app.callback(
        Output(f"buttonGroup-domain-selected-{i+1}", "hidden"),
        [Input(f"dashboard-card-domain-selection-{i+1}", "color")]
    )(generate_card_domain_button)'''
    


'''@app.callback(
    [Output("contract_monitor_card", "hidden"),
    Output("additional_monitor_card", "hidden"),
    Output("switch-contract-additional-view","children")],
    [Input("switch-contract-additional-view","n_clicks")]
)
def switch_monitor_view(n):    
    if n and n%2 == 1:
        return True, False, "Switch to Contract Monitor" 
        
    return False, True, "Switch to Additional Watchlist"
    '''
        
