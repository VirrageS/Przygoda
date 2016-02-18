from app import app, db
from app.miscellaneous import execution_time
from app.users.models import User
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.mine.models import AdventureViews, AdventureSearches
from math import expm1

def get_adventures_by_user_position(user_id, current_position):
    results = []

    # get all active adventures
    adventures = Adventure.objects.active_adventures()

    for adventure in adventures:
        # get add coordinates of adventure route
        coordinates = Adventure.objects.coordinates(adventure.id)

        # compute average distance from current position
        average_distance = 0.0
        for coordinate in coordinates:
            # calculate distance
            distance = abs(float(current_position['latitude']) - coordinate.latitude) ** 2
            distance += abs(float(current_position['longitude']) - coordinate.longitude) ** 2
            distance = distance ** (1/2)

            average_distance += distance

        # calculate average distance
        if coordinates:
            average_distance = average_distance / len(coordinates)

        results.append({
            'adventure_id': adventure.id,
            'distance': average_distance
        })

    # sort by distance
    results = sorted(results, key=(lambda result: result['distance']))

    # get positions in ranking
    positions = {}
    for idx, result in enumerate(results, start=1):
        positions[result['adventure_id']] = idx

    return positions

def get_adventures_by_friends(user_id):
    friends_ids = set() # set of friends user_ids

    # get all adventures to which user joined
    user_joined_adventures = Adventure.objects.user_joined_adventures()

    for adventure in user_joined_adventures:
        # check if creator exists
        creator = User.query.filter_by(id=adventure.creator_id).first()
        if creator is None:
            continue

        # get active participants
        participants = Adventure.objects.active_participants()

        # save participants as a friends
        for participant in participants:
            friends_ids.add(participant.user_id) # FIXME: change to touple (user_id, counter)


    results = [] # results of algorithm

    # get all active adventures
    adventures = Adventure.objects.active_adventures()

    for adventure in adventures:
        # get active participants
        paritcipants = Adventure.objects.active_participants(adventure.id)

        participants_ids = set()
        for participant in participants:
            participants_ids.add(participant.user_id)

        # get intersection of participants_ids and friends_ids
        friends_in_adventure = friends_ids & participants_ids

        results.append({
            'adventure_id': adventure.id,
            'friends_percent': len(friends_in_adventure) / len(participants) if len(participants) > 0 else 0,
            'friends_number': len(friends_in_adventure),
            'partcipants_number': len(participants)
        })

    # sort by friends percent
    results = sorted(results, key=(lambda result: result['friends_percent']))

    # get positions in ranking
    positions = {}
    for idx, result in enumerate(results, start=1):
        positions[result['adventure_id']] = idx

    return positions

def get_adventures_by_partcipants_number():
    results = []

    # get all active adventures
    adventure = Adventure.objects.active_adventures()
    for adventure in adventures:
        paritcipants = Adventure.objects.participants(adventure.id)
        results.append({
            'adventure_id': adventure.id,
            'partcipants_number': len(participants)
        })

    results = sorted(results, key=(lambda result: result['partcipants_number']))

    # get positions in ranking
    positions = {}
    for idx, result in enumerate(results, start=1):
        positions[result['adventure_id']] = idx

    return positions

def get_adventures_by_views():
    results = [] # final results

    # get all active adventures
    adventures = Adventure.objects.active_adventures()

    for adventure in adventures:
        views = AdventureViews.query.filter_by(adventure_id=adventure.id).all()

        counted_views = 0
        for view in views:
            counted_views += view.value

        results.append({
            'adventure_id': adventure.id,
            'views': counted_views
        })

    # sort results by views
    results = sorted(results, key=(lambda result: result['views']))

    # get positions in ranking
    positions = {}
    for idx, result in enumerate(results, start=1):
        positions[result['adventure_id']] = idx

    return positions

def get_adventures_by_searches():
    results = [] # final results

    # get all active adventures
    adventures = Adventure.objects.active_adventures()

    for adventure in adventures:
        searches = AdventureSearches.query.filter_by(
            adventure_id=adventure.id
        ).all()

        counted_searches = 0
        for search in searches:
            counted_searches += search.value

        results.append({
            'adventure_id': adventure.id,
            'searches': counted_searches
        })

    # sort results by views
    results = sorted(results, key=(lambda result: result['searches']))

    # get positions in ranking
    positions = {}
    for idx, result in enumerate(results, start=1):
        positions[result['adventure_id']] = idx

    return positions

def get_adventures_by_mode(user_id):
    results = []
    final_results = {}

    # get all adventures to which user joined
    user_joined_adventures = Adventure.objects.user_joined_adventures()

    for adventure in user_joined_adventures:
        # check if creator exists
        creator = User.query.filter_by(id=adventure.creator_id).first()
        if creator is None:
            continue


        results.append({
            'adventure_id': adventure.id,
            'mode': adventure.mode
        })

    # group results in modes
    for result in results:
        final_results[result['mode']].append(adventure.id)

    return final_results

# @execution_time
def get_recommended_adventures(user_id, user_position=None):
    # get all active adventures which has been created lately
    most_recent = Adventure.objects.active_adventures()
    sorted(most_recent, key=(lambda a: a.created_on), reverse=True)

    # get all active adventures which starts soon
    start_soon = Adventure.objects.active_adventures()
    sorted(start_soon, key=(lambda a: a.date), reverse=False)

    # if user is not logged we should not compute top_adventures
    if user_id is None:
        return {
            'most_recent': most_recent,
            'start_soon': start_soon,
            'top_adventures': most_recent
        }

    # check if position has been fetcheds
    adventures_by_position = {}
    if ((user_position is not None)
            and user_position['latitude'] and user_position['longitude']):
        adventures_by_position = get_adventures_by_user_position(
            user_id=user_id,
            current_position={
                'latitude': user_position['latitude'],
                'longitude': user_position['longitude']
            }
        )

    adventures_by_friends = get_adventures_by_friends(user_id=user_id)
    adventures_by_participants_number = get_adventures_by_partcipants_number()
    adventures_by_views = get_adventures_by_views()
    adventures_by_searches = get_adventures_by_searches()

    # get all active adventures
    # filter adventures which user has not created
    adventures = Adventure.objects.active_adventures()
    adventures = [adventure for adventure in adventures
                    if adventure.creator_id != user_id]

    # get only adventures to which user has not joined
    tmp_adventures = []
    for adventure in adventures:
        participant = AdventureParticipant.query.filter_by(
            adventure_id=adventure.id,
            user_id=user_id
        ).first()

        if participant is None:
            tmp_adventures.append(adventure)

    # assing filtered adventures
    adventures = tmp_adventures

    # compute score
    results = []
    for adventure in adventures:
        # get user_position score
        position_score = 1
        if adventure.id in adventures_by_position.keys():
            position_score = expm1(1/adventures_by_position[adventure.id]) * 2

        # get user_friends score
        friends_score = 1
        if adventure.id in adventures_by_friends.keys():
            friends_score = expm1(1/adventures_by_friends[adventure.id]) * 2

        # get adventure_participants_number score:
        participants_number_score = 1
        if adventure.id in adventures_by_participants_number.keys():
            participants_number_score = expm1(1/adventures_by_participants_number[adventure.id])

        # get views_score
        views_score = 1
        if adventure.id in adventures_by_views.keys():
            views_score = expm1(1/adventures_by_views[adventure.id]) * 0.1

        # get searches_score
        searches_score = 1
        if adventure.id in adventures_by_searches.keys():
            searches_score = expm1(1/adventures_by_searches[adventure.id]) * 0.1

        results.append({
            'adventure': adventure,
            'score': (position_score + friends_score
                      + participants_number_score + views_score
                      + searches_score)
        })

    # sort by score
    results = sorted(results, key=(lambda result: result['score']))

    # get only adventures
    top_adventures = [result['adventure'] for result in results]

    return {
        'most_recent': most_recent,
        'start_soon': start_soon,
        'top_adventures': top_adventures
    }
