#!/bin/bash


describe "Connect to fake server for testing"
	
	it "Connects to fake server"
		ssh root@localhost -p 2222 -o StrictHostKeyChecking=no mkdir haha
		assert equal "$(ssh root@localhost -p 2222 ls)" "haha"
	end
end

describe "Mounting"
	it "Mounts the fake server"
		fake_yaml=$(clusterutils path fake.yaml)
		printf "fakeserver:\n  user:root\n  hostname:localhost\n" > "${fake_yaml}"
                clusterutils setupcluster "${fake_yaml}" >/dev/null 2>/dev/null
                rm "${fake_yaml}"
		clusterutils mount fakeserver -p 2222
		assert equal "$(ls ${CLUSTER_UTILS_MOUNTS}/fakeserver)" "haha"
	end

	it "Removes write permissions from mounts dir"
		assert test "[ ! -w ${CLUSTER_UTILS_MOUNTS} ]"
	end

	it "Protects mountpoints from recursive deletions"
		chmod +w ${CLUSTER_UTILS_MOUNTS}
		rm -r ${CLUSTER_UTILS_MOUNTS}
		assert equal $(ls ${CLUSTER_UTILS_MOUNTS}/fakeserver) "haha"
		chmod -w ${CLUSTER_UTILS_MOUNTS}
	end

	it "Removes the fake server"
		clusterutils removecluster fakeserver
		assert equal "$(clusterutils lsmounts)" ""
	end

	it "Grants write permissions for empty mounts dir"
		assert test "[ -w ${CLUSTER_UTILS_MOUNTS} ]"	
	end
end


