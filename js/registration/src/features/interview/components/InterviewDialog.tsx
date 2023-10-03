import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog.js"
import { useInterviewState } from "#src/features/interview/hooks.js"
import { useWretch } from "#src/hooks/api.js"
import { useLocation, useNavigate } from "#src/hooks/location.js"
import { Skeleton, Text } from "@mantine/core"
import {
  ExitView,
  InterviewComponent,
  QuestionView,
} from "@open-event-systems/interview-components"
import { InterviewStateRecord } from "@open-event-systems/interview-lib"
import { FormValues } from "@open-event-systems/interview-lib"
import { action, runInAction } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { useCallback, useLayoutEffect, useState } from "react"
import { createPortal } from "react-dom"
import { WretchResponse } from "wretch"

export type InterviewDialogProps = {
  recordId?: string
  onSubmit: (values: FormValues) => Promise<void>
} & Omit<ModalDialogProps, "children" | "onSubmit" | "content">

export const InterviewDialog = (props: InterviewDialogProps) => {
  const { recordId, opened, onClose, onSubmit, ...other } = props

  const interviewStateStore = useInterviewState()

  const [titleEl, setTitleEl] = useState<HTMLElement | null>(() => null)
  const setRef = useCallback((el: HTMLElement | null) => {
    setTitleEl(el)
  }, [])

  return (
    <ModalDialog
      opened={opened}
      onClose={onClose}
      styles={{
        body: {
          minHeight: 400,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
          "& > *": {
            flex: "auto",
          },
        },
      }}
      title={<Text ref={setRef} span></Text>}
      {...other}
    >
      {recordId ? (
        <InterviewComponent
          key={recordId}
          recordId={recordId}
          stateStore={interviewStateStore}
          onSubmit={onSubmit}
          renderQuestion={(props, title) => (
            <>
              {titleEl ? createPortal(<>{title}</>, titleEl) : null}
              <QuestionView {...props} />
            </>
          )}
          renderExit={(props, title) => (
            <>
              {titleEl ? createPortal(<>{title}</>, titleEl) : null}
              <ExitView {...props} onClose={onClose} />
            </>
          )}
        />
      ) : (
        <>
          {titleEl
            ? createPortal(<Skeleton height={24} width={120} />, titleEl)
            : null}
          <Skeleton height={24} mt={6} />
          <Skeleton height={24} mt={6} />
          <Skeleton height={150} mt={30} />
        </>
      )}
    </ModalDialog>
  )
}

const Manager = observer(
  (
    props: {
      onComplete: (
        response: Promise<WretchResponse>,
        record: InterviewStateRecord,
      ) => Promise<void>
    } & Omit<
      InterviewDialogProps,
      "onSubmit" | "onClose" | "recordId" | "opened"
    >,
  ) => {
    const { onComplete, ...other } = props

    const wretch = useWretch()
    const loc = useLocation()
    const navigate = useNavigate()

    const interviewState = useInterviewState()

    const locState = loc.state?.showInterviewDialog
    const recordId = locState?.recordId

    const state = useLocalObservable(() => ({
      prevRecordId: recordId,
      submitting: false,
    }))

    const show = !!recordId

    useLayoutEffect(() => {
      if (recordId) {
        runInAction(() => {
          state.submitting = false
          state.prevRecordId = recordId
        })
      }
    }, [recordId])

    const handleClose = () => {
      navigate(loc, { state: { ...loc.state, showInterviewDialog: undefined } })
    }

    const handleSubmit = action(async (values: FormValues) => {
      if (!recordId || !locState) {
        return
      }

      const record = interviewState.getRecord(recordId)

      if (!record) {
        return
      }

      state.submitting = true

      try {
        const newRecord = await interviewState.updateInterview(record, values)

        if (
          newRecord.stateResponse.complete &&
          newRecord.stateResponse.target_url
        ) {
          const submitResponse = wretch
            .url(newRecord.stateResponse.target_url, true)
            .json({
              state: newRecord.stateResponse.state,
            })
            .post()
            .res()

          await onComplete(submitResponse, newRecord)
        } else {
          navigate(loc, {
            state: {
              ...loc.state,
              showInterviewDialog: {
                recordId: newRecord.id,
                eventId: locState.eventId,
              },
            },
          })
        }
      } catch (_) {
        runInAction(() => {
          state.submitting = false
        })
      }
    })

    const curRecordId = show ? recordId : state.prevRecordId

    return (
      <InterviewDialog
        recordId={curRecordId}
        opened={show}
        onClose={handleClose}
        onSubmit={handleSubmit}
        loading={state.submitting}
        {...other}
      />
    )
  },
)

Manager.displayName = "InterviewDialogManager"

InterviewDialog.Manager = Manager
