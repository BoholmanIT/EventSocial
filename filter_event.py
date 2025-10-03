from sqlalchemy import select, and_

def filter_event(session, data_from=None,data_to=None , place=None):
    query = select(Event)

    if data_from and data_to:
        query = query.where(Event.data_event.between(data_from, data_to))
    
    if place:
        query = query.where(Event.place.ilike(f"%{place}%"))
        
    result = session.execute(query).scalars.all()
    return result