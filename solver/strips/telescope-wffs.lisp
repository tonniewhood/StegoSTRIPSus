(in-package :user)

(reset-db)

;;; These are a set of backward chaining inference rules that are used by 
;;; STRIPS to determine what preconditions actually have to be met in order
;;; to get things down.

;;; Our predicates are:
;;;        INST       (the obvious)
;;;        SURFACE    (the surface of a bit or lens)
;;;        SHAPE      (the shape of an object)
;;;        SIZE       (the size of an object)
;;;
;;; We can also describe different states of machines and objects
;;;
;;;        SET       (a bit and a machine)
;;;        UNSET     (a machine <no bit in machine>)
;;;        MOUNTED   (a lens and a clamp)
;;;        OPEN      (a machine <no lens in clamp>)
;;;        POSS      (an object and an agent)
;;;        FREE      (an agent's hand)
;;;        AVAILABLE (any item not clamped or held)

;;; A telescope exists if there are two smooth lenses (one large and one small)
;;; and a tube.  Each lens must be attached to the tube.
                 
;;; Some facts about things in the world.

;;; FIRST OUR RAW MATERIALS

;;; There are some lenses
;;; We have a bunch of lenses.

(store '(inst blank2 lens))
(store '(inst blank3 lens))
;(store '(inst blank4 lens))

;;; They have rough surfaces.


(store '(surface blank2 rough))
(store '(surface blank3 rough))
;(store '(surface blank4 rough))


;;; They are flat.

(store '(shape blank2 flat))
(store '(shape blank3 flat))
;(store '(shape blank4 flat))

;;; Some are small, some are large.


(store '(size blank2 small))
(store '(size blank3 large))
;(store '(size blank4 large))

;;; They all start out available

(store '(available blank2))
(store '(available blank3))
;(store '(available blank4))

(store '(inst sheet1 sheet-metal))
;(store '(inst sheet2 sheet-metal))

;;; All sheet metal is flat.

(store '(-> (inst ?x sheet-metal) (shape ?x flat) ))

;;; And our two main peices of metal are available

(store '(available sheet1))
;(store '(available sheet2))

;;;; We also have metal strips and pieces of wood

(store '(inst strip2 strip))
(store '(inst stick2 wood))
(store '(available strip2))
(store '(available stick2))

;;; NEXT OUR MACHINES

;;; We have one each of a lathe, polisher, grinder and saw.
;;; All machines are OPEN and UNSET.

(store '(inst lathe1 lathe))
(store '(unset lathe1))
(store '(open lathe1))

(store '(inst polisher2 polisher))
(store '(unset polisher2))
(store '(open polisher2))

(store '(inst grinder3 grinder))
(store '(unset grinder3))
(store '(open grinder3))

(store '(inst saw4 saw))
(store '(unset saw4))
(store '(open saw4))

(store '(-> (and (isa ?x machine) (inst ?z ?x)) (inst ?z machine)))

(store '(isa saw machine))
(store '(isa lathe machine))
(store '(isa grinder machine))
(store '(isa polisher machine))

;;; AND WE HAVE SOME TOOLS

(store '(inst bit1 bit))
(store '(inst bit2 bit))

(store '(surface bit1 rough))
(store '(surface bit2 smooth))

(store '(available bit1))
(store '(available bit2))

;;; And our robot starts out with his hand free

(store '(free (hand-of robot)))
