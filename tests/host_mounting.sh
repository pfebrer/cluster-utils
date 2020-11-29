#!/bin/bash


describe "Connect to fake server for testing"
	
	it "Connects to fake server"
		ssh root@localhost -p 2222 -o StrictHostKeyChecking=no mkdir haha
		assert equal "$(ssh root@localhost -p 2222 ls)" "haha"
	end
end

describe "Mounting"
	it "Mounts the fake server"
		fake_yaml=$(_clupath fake.yaml)
		printf "fakeserver:\n  user: root\n  hostname: localhost\n" > "${fake_yaml}"
                clu setuphost --config "${fake_yaml}" --use-defaults >/dev/null 2>/dev/null
                rm "${fake_yaml}"
		clu mount fakeserver -p 2222
		assert equal "$(ls ${CLUSTER_UTILS_MOUNTS}/fakeserver)" "haha"
	end

	it "Removes write permissions from mounts dir"
		assert test "[ ! -w ${CLUSTER_UTILS_MOUNTS} ]"
	end

	describe "Listing mounts"
		
		it "Works with no mounts directory"
			assert equal "$(CLUSTER_UTILS_MOUNTS=$(_clupath non_EXISTEnT_dir__) clu lsmounts)" ""
		end

		it "Lists mounted fakeserver"
			assert equal "$(clu lsmounts)" "fakeserver"
		end

		it "Doesn't get fooled by unmounted dirs"
			chmod +w "${CLUSTER_UTILS_MOUNTS}"
			# Create some fake mountpoints
			mkdir -p "${CLUSTER_UTILS_MOUNTS}/test1" "${CLUSTER_UTILS_MOUNTS}/test2" 
			assert equal "$(clu lsmounts)" "fakeserver"
			# Remove all of them very safely
			rmdir "${CLUSTER_UTILS_MOUNTS}/test1" "${CLUSTER_UTILS_MOUNTS}/test2"
			chmod -w "${CLUSTER_UTILS_MOUNTS}"
		end
		
	end

	it "Protects mountpoints from recursive deletions"
		chmod +w ${CLUSTER_UTILS_MOUNTS}
		rm -r ${CLUSTER_UTILS_MOUNTS}
		assert equal $(ls ${CLUSTER_UTILS_MOUNTS}/fakeserver) "haha"
		chmod -w ${CLUSTER_UTILS_MOUNTS}
	end

	it "Removes the fake server"
		clu removehost fakeserver
		assert equal "$(clu lsmounts)" ""
	end

	it "Grants write permissions for empty mounts dir"
		assert test "[ -w ${CLUSTER_UTILS_MOUNTS} ]"	
	end

end


