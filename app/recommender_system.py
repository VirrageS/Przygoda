from app import app, db
from app.adventures.models import Adventure, Coordinate, AdventureParticipant

def get_adventures_by_user_position(user_id, current_position):
	results = []

	adventures = Adventure.query.all() # get all adventures
	adventures = [adventure for adventure in adventures if adventure.is_active()] # get all active adventures

	for adventure in adventures:
		# get add coordinates of adventure route
		coordinates = Coordinate.query.filter_by(adventure_id=adventure.id).all()

		# compute average distance from current position
		average_distance = 0.0
		for coordinate in coordinates:
			# calculate distance
			distance = abs(current_position['latitude'] - coordinate.latitude) ** 2
			distance += abs(current_position['longitude'] - coordinate.longitude) ** 2
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
	return results

def get_adventures_by_friends(user_id):
	friends_ids = set() # set of friends user_ids

	# get all adventures to which user joined
	adventures_participant = AdventureParticipant.query.filter_by(user_id=user_id).all()
	joined_adventures_ids = [participant.adventure_id for participant in adventures_participant if participant.is_active()]

	for joined_adventures_id in joined_adventures_ids:
		# check if adventure ever existed
		adventure = Adventure.query.filter_by(id=joined_adventures_id).first()
		if adventure is None:
			continue

		# check if creator exists
		creator = User.query.filter_by(id=adventure.creator_id).first()
		if creator is None:
			continue


		# get active participants
		participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
		participants = [participant for participant in participants if participant.is_active()]

		# save participants as a friends
		for participant in participants:
			friends_ids.add(participant.user_id) # FIXME: change to touple (user_id, counter)


	results = [] # results of algorithm

	adventures = Adventure.query.all() # get all adventures
	adventures = [adventure for adventure in adventures if adventure.is_active()] # get all active adventures
	for adventure in adventures:
		# get active participants
		participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
		participants = [participant for participant in participants if participant.is_active()]

		participants_ids = set()
		for participant in participants:
			participants_ids.add(participant.user_id)

		# get intersection of participants_ids and friends_ids
		friends_in_adventure = friends_ids & participants_ids

		results.append({
			'adventure_id': adventure.id,
			'friends_percent': len(friends_in_adventure) / len(partcipants),
			'friends_number': len(friends_in_adventure),
			'partcipants_number': len(participants)
		})

	# sort by friends percent
	results = sorted(results, key=(lambda result: result['friends_percent']))

	return results

def get_adventures_by_number_of_participants():
	results = []

	adventures = Adventure.query.all() # get all adventures
	adventures = [adventure for adventure in adventures if adventure.is_active()] # get all active adventures

	for adventure in adventures:
		participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()

		results.append({
			'adventure_id': adventure.id,
			'number_of_participants': len(participants)
		})

	results = sorted(results, key=(lambda result: result['number_of_participants']))
	return final_adventures

def get_adventures_by_mode(user_id):
	results = []
	final_results = {}

	# get all adventures to which user joined
	adventures_participant = AdventureParticipant.query.filter_by(user_id=user_id).all()
	joined_adventures_ids = [participant.adventure_id for participant in adventures_participant if participant.is_active()]

	for joined_adventures_id in joined_adventures_ids:
		# check if adventure exists and is active
		adventure = Adventure.query.filter_by(id=joined_adventures_id).first()
		if adventure is None:
			continue

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


def get_recommended_adventures(user_id):
	most_recent = Adventure.query.order_by(Adventure.created_on.desc()).all() # get all adventures
	most_recent = [adventure for adventure in most_recent if adventure.is_active()] # get all active adventures

	start_soon = Adventure.query.order_by(Adventure.date.asc()).all() # get all adventures
	start_soon = [adventure for adventure in start_soon if adventure.is_active()] # get all active adventures

	if user_id is None:
		top_adventures = most_recent
	else:
		top_adventures = most_recent

	return {
		'most_recent': most_recent,
		'start_soon': start_soon,
		'top_adventures': top_adventures
	}
