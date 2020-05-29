import logging

import requests

import util

from typing import Dict, Optional
from uuid import UUID

from requests.auth import AuthBase

from jobs import Application

_LOG = logging.getLogger(__name__)
_LOG.addHandler(logging.StreamHandler())

_COOK_IMPERSONATE_HEADER = 'X-Cook-Impersonate'

_DEFAULT_STATUS_UPDATE_INTERVAL_SECONDS = 10
_DEFAULT_BATCH_REQUEST_SIZE = 32
_DEFAULT_REQUEST_TIMEOUT_SECONDS = 60
_DEFAULT_SUBMIT_RETRY_INTERVAL_SECONDS = 10
_DEFAULT_DELETE_ENDPOINT = '/rawscheduler'


class InstanceDecorator:
    def decorate(self, inst_args: dict) -> dict:
        raise NotImplementedError("stub")


class JobClient:
    __host: str
    __port: int

    __job_uri: str
    __delete_uri: str
    __group_uri: str

    __status_update_interval: int = _DEFAULT_STATUS_UPDATE_INTERVAL_SECONDS
    __submit_retry_interval: int = _DEFAULT_SUBMIT_RETRY_INTERVAL_SECONDS
    __batch_request_size: int = _DEFAULT_BATCH_REQUEST_SIZE
    __request_timeout_seconds: int = _DEFAULT_REQUEST_TIMEOUT_SECONDS

    def __init__(self, host: str, port: int, *,
                 job_endpoint: str,
                 delete_endpoint: str):
        self.__host = host
        self.__port = port
        self.__job_uri = f'http://{host}:{port}/{job_endpoint}'
        self.__delete_uri = f'http://{host}:{port}/{delete_endpoint}'

    def submit(self, *,
               command: str,
               cpus: float,
               mem: float,

               uuid: Optional[UUID] = None,
               env: Optional[Dict[str, str]] = None,
               labels: Optional[Dict[str, str]] = None,
               max_runtime: Optional[int] = None,
               name: Optional[str] = None,
               priority: Optional[int] = None,
               application: Optional[Application] = None) -> UUID:
        """Submit a single job to Cook.

        :param command: The command to run on Cook.
        :type command: str
        :param cpus: The number of CPUs to request from Cook.
        :type cpus: float
        :param mem: The amount of memory, in GB, to request from Cook.
        :type mem: float
        :param uuid: The UUID of the job to submit. If this value is not
            provided, then a random UUID will be generated.
        :type uuid: UUID, optional
        :param env: Environment variables to set within the job's context,
            defaults to None.
        :type env: Dict[str, str], optional
        :param labels: Labels to assign to the job, defaults to None.
        :type labels: Dict[str, str], optional
        :param max_runtime: The maximum number seconds this job should be
            allowed to run, defaults to None.
        :type max_runtime: int, optional
        :param name: A name to assign to the job, defaults to None.
        :type name: str, optional
        :param priority: A priority to assign to the job, defaults to None.
        :type priority: int, optional
        :param application: Application information to assign to the job,
            defaults to None.
        :type application: Application, optional
        :return: The UUID of the newly-created job.
        :rtype: UUID
        """
        payload = {
            'command': command,
            'cpus': cpus,
            'mem': mem,
            'uuid': uuid if uuid is not None else util.make_temporal_uuid()
        }
        if env is not None:
            payload['env'] = env
        if labels is not None:
            payload['labels'] = labels
        if max_runtime is not None:
            payload['max_runtime'] = max_runtime
        if name is not None:
            payload['name'] = name
        if priority is not None:
            payload['priority'] = priority
        if application is not None:
            payload['application'] = application.to_dict()

        resp = requests.post(self.__job_uri, json=payload)
        resp.raise_for_status()

        return payload['uuid']

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def job_uri(self) -> str:
        return self.__job_uri

    @property
    def delete_uri(self) -> str:
        return self.__delete_uri

    @property
    def group_uri(self) -> str:
        return self.__group_uri

    @property
    def status_update_interval(self) -> int:
        return self.__status_update_interval

    @property
    def submit_retry_interval(self) -> int:
        return self.__submit_retry_interval

    @property
    def batch_request_size(self) -> int:
        return self.__batch_request_size

    @property
    def request_timeout_seconds(self) -> int:
        return self.__request_timeout_seconds

    @property
    def instance_decorator(self) -> Optional[InstanceDecorator]:
        return self.__instance_decorator

    @property
    def auth(self) -> Optional[AuthBase]:
        return self.__auth