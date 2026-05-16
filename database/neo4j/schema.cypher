CREATE CONSTRAINT entity_key IF NOT EXISTS FOR (e:Entity) REQUIRE e.key IS UNIQUE;
CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type);
CREATE INDEX entity_normalized IF NOT EXISTS FOR (e:Entity) ON (e.normalized);

// Relationship examples:
// (:Entity {type:'email'})-[:USES]->(:Entity {type:'username'})
// (:Entity {type:'username'})-[:OWNS]->(:Entity {type:'social_profile'})
// (:Entity {type:'domain'})-[:HOSTS]->(:Entity {type:'ip_address'})
