import {
  createStyles,
  DefaultProps,
  Modal,
  ModalProps,
  Selectors,
  Text,
  useComponentDefaultProps,
} from "@mantine/core"
import {
  FormValues,
  InterviewStateStore,
} from "@open-event-systems/interview-lib"
import { Observer, observer, useLocalObservable } from "mobx-react-lite"
import { ExitView, ExitViewProps } from "#src/components/interview/ExitView.js"
import {
  QuestionView,
  QuestionViewProps,
} from "#src/components/interview/QuestionView.js"
import { InterviewComponent } from "#src/components/interview/InterviewComponent.js"
import { createPortal } from "react-dom"

const dialogStyles = createStyles({
  root: {},
  title: {},
  question: {},
  exit: {},
})

export type InterviewDialogProps = {
  /**
   * The current state record ID.
   */
  recordId: string

  /**
   * The {@link InterviewStateStore}.
   */
  stateStore: InterviewStateStore

  /**
   * The form submit handler.
   */
  onSubmit: (values: FormValues) => Promise<void>

  /**
   * Props passed down to the {@link QuestionView} component.
   */
  QuestionViewProps?: Partial<QuestionViewProps>

  /**
   * Props passed down to the {@link ExitView} component.
   */
  ExitViewProps?: Partial<ExitViewProps>
} & DefaultProps<Selectors<typeof dialogStyles>> &
  Omit<ModalProps, "children" | "title" | "onSubmit" | "styles">

/**
 * A component that renders interview content in a dialog.
 */
export const InterviewDialog = observer((props: InterviewDialogProps) => {
  const {
    styles,
    unstyled,
    className,
    classNames,
    recordId,
    stateStore,
    onSubmit,
    onClose,
    QuestionViewProps,
    ExitViewProps,
    ...other
  } = useComponentDefaultProps("OESIInterviewDialog", {}, props)

  const { classes, cx } = dialogStyles(undefined, {
    name: "OESIInterviewDialog",
    classNames,
    styles,
    unstyled,
  })

  const state = useLocalObservable(() => ({
    titleEl: null as HTMLElement | null,
    setRef(el: HTMLElement | null) {
      this.titleEl = el
    },
  }))

  return (
    <Modal
      className={cx(classes.root, className)}
      {...other}
      onClose={onClose}
      title={<Text ref={state.setRef} span></Text>}
    >
      <InterviewComponent
        key={recordId}
        recordId={recordId}
        onSubmit={onSubmit}
        stateStore={stateStore}
        renderQuestion={(props, title) => (
          <Observer>
            {() => (
              <>
                {state.titleEl
                  ? createPortal(<>{title}</>, state.titleEl)
                  : null}
                <QuestionView
                  className={classes.question}
                  {...QuestionViewProps}
                  {...props}
                />
              </>
            )}
          </Observer>
        )}
        renderExit={(props, title) => (
          <Observer>
            {() => (
              <>
                {state.titleEl
                  ? createPortal(<>{title}</>, state.titleEl)
                  : null}
                <ExitView
                  className={classes.exit}
                  onClose={onClose}
                  {...ExitViewProps}
                  {...props}
                />
              </>
            )}
          </Observer>
        )}
      />
    </Modal>
  )
})
