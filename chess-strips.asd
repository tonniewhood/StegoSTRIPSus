
;;;; chess-strips.asd

(defsystem "chess-strips"
  :description "Chess endgame STRIPS solver with steganography"
  :author "Anthony Wood"
  :components 
  (;; Load STRIPS infrastructure first
   (:module "strips"
    :pathname "solver/strips/"
    :components ((:file "for")
                 (:file "pc")
                 (:file "index")
                 (:file "unify")
                 (:file "database")
                 (:file "store")
                 (:file "show")
                 (:file "binding-structure")
                 (:file "srules")
                 (:file "strips")))
   
   ;; Then load problem definition
   (:module "solver"
    :pathname "solver/"
    :components ((:file "endgame.wff")
                 (:file "endgame.op")
                 (:file "solve")))))