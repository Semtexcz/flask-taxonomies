from flask_taxonomies.utils import link_self


def test_link_self(db, root_taxonomy):
    leaf = root_taxonomy.create_term(slug="leaf",
                                     extra_data="extra_data")

    db.session.refresh(root_taxonomy)
    db.session.refresh(leaf)

    assert link_self("root", leaf) == "https://localhost/api/taxonomies/root/leaf"
