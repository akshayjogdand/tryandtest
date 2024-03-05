def clone_rule(rule, new_rule_klass):
    new_rule = new_rule_klass()
    for field in rule._meta.fields:
        attr_name = field.attname
        setattr(new_rule, attr_name, getattr(rule, attr_name))

    new_rule.id = None
    new_rule.parent_rule = rule

    return new_rule


def update_cloned_rule(parent_rule, cloned_rule):
    clone_id = cloned_rule.id
    for field in parent_rule._meta.fields:
        attr_name = field.name
        setattr(cloned_rule, attr_name, getattr(parent_rule, attr_name))

    cloned_rule.id = clone_id
