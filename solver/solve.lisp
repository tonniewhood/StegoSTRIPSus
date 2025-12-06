;;;; run_strips.lisp
;;;; Command-line interface for STRIPS solver
;;;; Usage: sbcl --script run_strips.lisp <goal>
;;;;   or:  clisp run_strips.lisp <goal>

(in-package :user)


;; Load the STRIPS system
(load "solver/strips/loader.lisp")
(load-strips)

;; Suppress STORE messages
(setf *quiet-db* t)

;; Get command-line arguments
(defparameter args
      #+sbcl sb-ext:*posix-argv*
       #+clisp ext:*args*
       #+ccl ccl:*command-line-argument-list*
       #-(or sbcl clisp ccl) (error "Unsupported Lisp implementation"))

;; Load world state and operators
(load (car args))
(load "solver/endgame.op")

;; Disable debug output for cleaner parsing
(strips-debug nil)

(defun format-plan-for-python (plan)
  "Format the plan in a way that's easy for Python to parse"
  (format t "===BEGIN_PLAN===~%")
  (dolist (op (reverse plan))
    (format t "~S~%" (op-action op)))
  (format t "===END_PLAN===~%"))

(defun main ()
  "Main entry point"
  (format t "[STRIPS] Solving for CHECKMATE...~%")
  (handler-case
      (let ((plan (strips '(CHECKMATE) t))) ; silent mode 
      (format t "[STRIPS] Planning complete.~%")
      (if plan
          (progn
              (format t "[STRIPS] Solution found!~%")
              (format-plan-for-python plan)
              #+sbcl (sb-ext:exit :code 0)
              #+clisp (ext:exit 0)
              #+ccl (ccl:quit 0))
          (progn
              (format t "[STRIPS] No solution found~%")
              #+sbcl (sb-ext:exit :code 1)
              #+clisp (ext:exit 1)
              #+ccl (ccl:quit 1))))
  (error (e)
      (format t "[STRIPS] Error: ~A~%" e)
      #+sbcl (sb-ext:exit :code 2)
      #+clisp (ext:exit 2)
      #+ccl (ccl:quit 2))))

;; Run main
(main)

