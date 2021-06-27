(define (domain craft-bots)

    (:requirements :typing)

    (:types
        waypoint - object
        resource-type - object
        locatable - object

        actor - locatable
        building - locatable
    )

    (:constants
        red blue orange green black - resource-type
    )

    (:predicates
        (at ?l - locatable ?w - waypoint)
        (connected ?a ?b - waypoint)
        (mine-at ?w - waypoint ?t - resource-type)
        (not-started ?b - building)
        (started ?b - building)
        (completed ?b - building)
    )

    (:functions
        (inventory ?a - actor ?t - resource-type)
        (waypoint-resources ?w - waypoint ?t - resource-type)
        (building-requirements ?b - building ?t - resource-type)
        (building-total-requirements ?b - building)
    )

    (:action move
        :parameters (?a - actor ?from ?to - waypoint)
        :precondition (and
            (at ?a ?from)
            (connected ?from ?to)
            )
        :effect (and
            (not (at ?a ?from))
            (at ?a ?to)
            )
    )

    (:action mine
        :parameters (?a - actor ?w - waypoint ?t - resource-type)
        :precondition (and
            (at ?a ?w)
            (mine-at ?w ?t)
            )
        :effect (and
            (increase (waypoint-resources ?w ?t) 1)
            )
    )

    (:action pick-up
        :parameters (?a - actor ?w - waypoint ?t - resource-type)
        :precondition (and
            (at ?a ?w)
            (> (waypoint-resources ?w ?t) 0)
            )
        :effect (and
            (decrease (waypoint-resources ?w ?t) 1)
            (increase (inventory ?a ?t) 1)
            )
    )

    (:action drop
        :parameters (?a - actor ?w - waypoint ?t - resource-type)
        :precondition (and
            (at ?a ?w)
            (> (inventory ?a ?t) 0)
            )
        :effect (and
            (decrease (inventory ?a ?t) 1)
            (increase (waypoint-resources ?w ?t) 1)
            )
    )

    (:action start-building
        :parameters (?a - actor ?w - waypoint ?b - building)
        :precondition (and
            (at ?a ?w)
            (at ?b ?w)
            (not-started ?b)
            )
        :effect (and
            (started ?b)
            (not (not-started ?b))
            )
    )

    (:action deposit
        :parameters (?a - actor ?w - waypoint ?b - building ?t - resource-type)
        :precondition (and
            (at ?a ?w)
            (at ?b ?w)
            (started ?b)
            (> (inventory ?a ?t) 0)
            (> (building-requirements ?b ?t) 0)
            )
        :effect (and
            (decrease (inventory ?a ?t) 1)
            (decrease (building-total-requirements ?b) 1)
            (decrease (building-requirements ?b ?t) 1)
            )
    )

    (:action complete-building
        :parameters (?a - actor ?w - waypoint ?b - building)
        :precondition (and
            (at ?a ?w)
            (at ?b ?w)
            (started ?b)
            (= (building-total-requirements ?b) 0)
            )
        :effect (and
            (completed ?b)
            )
    )
)