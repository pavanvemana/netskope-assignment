import yaml

def get_sla_targets(tier, priority):
    '''
    Function to get SLA targets based on 
    pre-defined values
    '''
    sla_config = {}
    with open('sla_config.yaml', 'r') as fp:
        sla_config = yaml.load(fp, Loader=yaml.FullLoader)
    return sla_config.get(tier, {}).get(priority, {})