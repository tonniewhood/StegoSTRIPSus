(in-package :user)

;;; Operators for the construction of a telescope.
;;;
;;; We have the following operators:
;;;  
;;;   GRIND            => shapes lenses
;;;   POLISH           => smooths lenses
;;;   SETUP            => places a bit into a machine
;;;   BREAK-DOWN       => removes a bit from a machine
;;;   MOUNT            => clamp a lens into a machine
;;;   DISMOUNT         => unclamp a lens
;;;   WRAP             => rolls a sheet into a tube
;;;   ATTACH           => attatch a lens to a tube
;;;   GRASP            => get possession of an item
;;;   UNGRASP          => let an item be available again.

;;; GRIND is an operation on a LENS, GRINDER.
;;; It requires that a BIT is set in the GRINDER and that
;;; the BLANK is in the mount.

;;; It is not considered if it is unable to find a flat lens blank, 
;;; grinder and rough bit.

;;; It results in the blank becoming a convex lens with a rough surface.
;;; The blank is no longer a flat lens and its old surface is gone.

(reset-op-index)

(def-operator telescope
    :action (no-op)
    :goal (inst (assembly ?l1 ?t) telescope)
    :precond ((inst ?l1 lens)
	      (size ?l1 large)
	      (shape ?l1 convex)
	      (inst ?l2 lens)
	      (size ?l2 small)
	      (shape ?l2 convex)
	      (surface ?l1 smooth)
	      (surface ?l2 smooth)
	      (inst ?t tube)
	      (attached ?l1 ?t (assembly ?l1 ?t))
	      (attached ?l2 (assembly ?l1 ?t) ?x))
    :filter ()
    :add ()
    :del ())

(def-operator grind
    :action (grind ?blank ?grinder)
    :goal (shape ?blank convex)
    :precond ((set ?grinder ?bit)
	      (mounted ?blank ?grinder))
    :filter ((inst ?blank lens)
	     (shape ?blank flat)
	     (inst ?grinder grinder)
	     (inst ?bit bit)
	     (surface ?blank ?texture)
	     (surface ?bit rough))
    :add ((surface ?blank rough))
    :del ((shape ?blank flat)
	  (surface ?blank ?texture)))

;;; POLISH is an operation on a lens, and GRINDER.
;;; It requires that a BIT is set in the GRINDER and that
;;; the BLANK is in the mount.

;;; It is not considered if it is unable to find a flat lens blank, 
;;; grinder and smooth bit.

;;; It adds a smooth surface.

(def-operator polish
    :action (polish ?blank ?polisher)
    :goal (surface ?blank smooth)
    :precond ((set ?polisher ?bit)
	      (mounted ?blank ?polisher))
    :filter ((inst ?blank lens)
	     (surface ?blank rough)
	     (inst ?polisher polisher)
	     (inst ?bit bit)
	     (surface ?bit smooth))
    :add ()
    :del ((surface ?blank rough)))

;;; SETUP sets a grinder or polisher up by installing a bit.

;;; It can be run if there the machine is unset and the ROBOT has a 
;;; bit. It is not run on anything but machines and bits.
;;; Once run, the machine and bit are SET.
;;; It removes the fact that the machine is unset and that the ROBOT 
;;; has possesion of the bit.

(def-operator setup
    :action (setup ?bit ?machine)
    :goal (set ?machine ?bit)
    :precond ((poss robot ?bit)
	      (unset ?machine))
    :filter ((inst ?machine machine)
	     (inst ?bit bit))
    :add ((free (hand-of robot)))
    :del ((unset ?machine)
	  (poss robot ?bit)))

;;; Break-down removes a bit from a machine.

;;; It can be run if there the machine is set..
;;; It is not run on anything but machines and bits.
;;; Once run, the machine is UNSET and bit is available.
;;; It removes the fact that the machine and bit are SET.

(def-operator break-down1
    :action (break-down ?bit ?machine)
    :goal (unset ?machine)
    :precond ()
    :filter ((set ?machine ?bit)
	     (inst ?machine machine)
	     (inst ?bit bit))
    :add ((available ?bit))
    :del ((set ?machine ?bit)))

(def-operator break-down2
    :action (break-down ?bit ?machine)
    :goal (available ?bit)
    :precond ()
    :filter ((set ?machine ?bit)
	     (inst ?machine machine)
	     (inst ?bit bit))
    :add ((unset ?machine))
    :del ((set ?machine ?bit)))

;;; MOUNT is an operation on a lens and machine.
;;; It requires the the robot has a lens and that the machine is open.

;;; It adds the fact that the lens is mounter in the machine and that 
;;; the robot's hand is free.

;;; Once done, the robot no longer has the blank and the machine is no
;;; longer open.

(def-operator mount
    :action (mount ?blank ?machine)
    :goal (mounted ?blank ?machine)
    :precond ((poss robot ?blank)
	      (open ?machine))
    :filter ((inst ?blank lens)
	     (inst ?machine machine))
    :add ((free (hand-of robot)))
    :del ((poss robot ?blank)
	  (open ?machine)))

;;; DISMOUNT undoes the effects of MOUNT.

;;; It has not preconditions, but is not run on a unmounted machine.

(def-operator dismount1
    :action (dismount ?blank ?machine)
    :goal (open ?machine)
    :precond ()
    :filter ((mounted ?blank ?machine)
	     (inst ?blank lens)
	     (inst ?machine machine))
    :add ((available ?blank))
    :del ((mounted ?blank ?machine)))

(def-operator dismount2
   :action (dismount ?blank ?machine)
   :goal (available ?blank)
   :precond ()
   :filter ((mounted ?blank ?machine)
	    (inst ?blank lens)
	    (inst ?machine machine))
   :add ((open ?machine))
   :del ((mounted ?blank ?machine)))


;;; GRASP has the effect of making the agent in possession of its argument.
;;; The agent's hand has to be free and the thing has to be available.

(def-operator grasp
    :action (grasp ?agent ?item)
    :goal (poss ?agent ?item)
    :precond ((free (hand-of ?agent))
	      (available ?item))
    :filter ()
    :add ()
    :del ((available ?item)
	  (free (hand-of ?agent))))

;;; UNGRASP reverses the effects of GRASP.

(def-operator ungrasp1
    :action (ungrasp ?agent ?item)
    :goal (available ?item)
    :precond ()
    :filter ((poss ?agent ?item))
    :add ((free (hand-of ?agent)))
    :del ((poss ?agent ?item)))

(def-operator ungrasp2
    :action (ungrasp ?agent ?item)
    :goal (free (hand-of ?agent))
    :precond ()
    :filter ((poss ?agent ?item))
    :add ((available ?item))
    :del ((poss ?agent ?item)))

;;; WRAP is performed on a piece of sheet metal and results in a tube.

(def-operator wrap 
    :action (wrap ?sheet)
    :goal (inst ?sheet tube)
    :precond ((poss robot ?sheet))
    :filter ((inst ?sheet sheet-metal))
    :add ()
    :del ((inst ?sheet sheet-metal)))

;;; ATTACH is performed on two items.  It results in them becoming attached.
;;; Once attached, an item is unavailable.

(def-operator attach1
    :action (attach ?one ?two)
    :goal (attached ?one ?two (assembly ?one ?two))
    :precond ((available ?one)
	      (available ?two))
    :filter ()
    :add ((available (assembly ?one ?two)))
    :del ((available ?one)
	  (available ?two)))

(def-operator attach2
    :action (attach ?one ?two)
    :goal (available (assembly ?one ?two))
    :precond ((available ?one)
	      (available ?two))
    :filter ()
    :add ((attached ?one ?two (assembly ?one ?two)))
    :del ((available ?one)
	  (available ?two)))
  
;;; DETACH is performed on a compound item.  It requires that the item was
;;; built out of an existing pair.

(def-operator detach1
    :action (detach (assembly ?one ?two))
    :goal (available ?one)
    :precond ((available (assembly ?one ?two)))
    :filter ((attached ?one ?two (assembly ?one ?two)))
    :add ((available ?two))
    :del ((attached ?one ?two (assembly ?one ?two))
	  (available (assembly ?one ?two))))

(def-operator detach2
    :action (detach (assembly ?one ?two))
    :goal (available ?two)
    :precond ((available (assembly ?one ?two)))
    :filter ((attached ?one ?two (assembly ?one ?two)))
    :add ((available ?one))
    :del ((attached ?one ?two (assembly ?one ?two))
	  (available (assembly ?one ?two))))
  
