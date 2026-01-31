# # backend/core/jobs/text_dispatcher.py
# from backend.core.base_service import TraceableService
# from backend.core.providers.queue_provider import get_queue
# from backend.core.config import Settings

# class TextDispatcherService (TraceableService):
#     """
#     Dispatcher for text-evaluation jobs.
#     Enqueue-by-reference: expects a job_id (TasksRepository document _id).
#     """
#     def __init__(self, queue_name: str | None = None):
#         self.queue = get_queue(name=queue_name)

#     def dispatch_text_evaluation(self, job_id: str):
#         """
#         Enqueue job_id so the worker will call:
#         backend.core.job_processors.process_evaluate_transcription_job.process_job_wrapper(job_id)
#         """
#         # Use fully-qualified string to avoid pickling/import order issues across processes
#         self.queue.enqueue(
#             "backend.core.job_processors.process_evaluate_transcription_job.process_job_wrapper",
#             job_id
#         )
#         # Replace print with metric/trace in production
#         print(f"[DISPATCHER] Enqueued text evaluation job for job_id={job_id}")



