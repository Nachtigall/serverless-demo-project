FROM public.ecr.aws/lambda/python:3.8 as stage

# Hack to install chromium dependencies
RUN yum install -y -q sudo unzip

ENV CHROMIUM_VERSION=1002910

# Install Chromium
COPY app/install-browser.sh /tmp/
RUN /usr/bin/bash /tmp/install-browser.sh

FROM public.ecr.aws/lambda/python:3.8 as base

COPY app/chrome-deps.txt /tmp/
RUN yum install -y $(cat /tmp/chrome-deps.txt)

COPY Pipfile Pipfile.lock app/ ${LAMBDA_TASK_ROOT}
# Install Python dependencies for function
RUN pip install pipenv
RUN pipenv install --system --deploy


COPY --from=stage /opt/chrome /opt/chrome
COPY --from=stage /opt/chromedriver /opt/chromedriver


CMD [ "app.handler" ]